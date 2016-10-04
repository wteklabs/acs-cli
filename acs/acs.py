"""
An instance of the Azure Container Service.
"""
from .AgentPool import AgentPool
from .AcsUtils import AcsUtils
from .dcos import Dcos
import json
import os.path
from subprocess import call
import paramiko
from paramiko import SSHClient
from paramiko.agent import AgentRequestHandler
import socket
import subprocess, os
import sys  
from tempfile import mkstemp
from sshtunnel import SSHTunnelForwarder
import signal
import time
from time import sleep
import urllib.request
from shutil import move
from os import remove, close

class Acs:
    def __init__(self, config):
        self.config = config
        self.utils = AcsUtils()
        self.logger = self.utils.getLogger("Acs")
        
    def exists(self):
        """ Tests whether the management endpoint is accessible, if it is we assume the service exists """
        exists = self._hostnameResolves(self.getManagementEndpoint())
        return exists

    def create(self):
        if self.exists():
            msg = "It appears that the cluster already exists:\n" + self.show()
            self.logger.debug(msg)
            return msg

        self.logger.debug("Creating ACS Deployment")
        self.logger.debug(json.dumps(self.config.getACSParams()))

        self.createResourceGroup()
    
        self._deploy(self.config.get('ACS', 'dnsPrefix'))
    
        if self.exists():
            if self.config.get('ACS', 'orchestratorType') == 'DCOS':
                dcos = Dcos(self)
                dcos.install_cli()

        return self.show()

    def _deploy(self, deploymentName):
        command = "azure group deployment create"
        command = command + " " + self.config.get('Group', 'name')
        command = command + " " + deploymentName
        command = command + " --template-uri " + self.config.get('Template', 'templateUrl')
        command = command + " -p '" + json.dumps(self.config.getACSParams()) + "'"
        os.system(command)

    def delete(self, quiet = False):
        self.logger.debug("Deleting ACS Deployment")
        self.logger.debug(json.dumps(self.config.getACSParams()))
    
        dns = self.config.get("ACS", "dnsPrefix")
        group = self.config.get("Group", "name")
        if not quiet and not self.args["--quiet"]:
            responded = False
            while not responded:
                resp = input("Do you really want to delete the ACS cluster '" + dns + "' in resource group '" + group + "' ('y' or 'yes' to confirm, 'n' or 'no' to abort)?\n")
                if resp == "y" or resp == "yes":
                    responded = True
                elif resp == "n" or resp == "no":
                    self.logger.debug("Aborting delete at users request")
                    return "Delete aborted"
        
        command = "azure acs delete"
        command = command + " " + group
        command = command + " containerservice-" + self.config.get('ACS', 'dnsPrefix')
        os.system(command)
    
        # FIXME: we shouldn't need to do the group delete, but currently container delete is not a deep delete
        self.logger.warning("'azure acs delete 'does not currently delete resources created within the container service. You can delete all resources by also deleting the associated resource group, however, be aware this will delete everything in the resource group.")
        command = "azure group delete " 
        if quiet or self.args["--quiet"]:
            command = command + " --quiet "
        command = command + self.config.get('Group', 'name')
        os.system(command)

    def scale(self, desired_agents):
        """ Scale the cluster """
        if not self.exists():
            return "It appears that the cluster does not exists (try running `acs service createo`)"

        fh, abs_path = mkstemp()
        with open(abs_path,'w') as new_file:
            with open(self.config.filename) as old_file:
                for line in old_file:
                    if line.startswith("agentCount:"):
                        new_file.write("agentCount: " + str(desired_agents) + "\n")
                    else:
                        new_file.write(line)
        close(new_file)
        close(fh)
        try:
            remove(self.config.filename + ".bak")
        except OSError:
            pass
        move(self.config.filename, self.config.filename + ".bak")
        move(abs_path, self.config.filename)

        self._deploy("scale")
    
        return "Scaled to " + str(desired_agents)

    def show(self):
        """
        Output the configuration of this cluster in json format.
        """
        config = self.getClusterSetup()
        return json.dumps(config, sort_keys=True,
                          indent=4, separators=(',', ': '))

    def deallocate(self):
        """
        Deallocate all VM and VMSS inside the cluster.
        """
        self.logger.debug("Shuting down VM and VMSS")
        commandListVm = "azure vm list -g " + self.config.get('Group', 'name') + " --json"
        VMresult = self.utils.shell_execute(commandListVm)
        jsonVMresult = json.loads(VMresult[0])
        for indexVM in range(len(jsonVMresult)):
            self.logger.info("Shuting down : " + jsonVMresult[indexVM]['name'])
            commandShutVm = "azure vm deallocate -g " + self.config.get('Group', 'name') + " -n " + jsonVMresult[indexVM]['name']
            self.utils.shell_execute(commandShutVm)

        commandListVmss = "azure vmss list -g " + self.config.get('Group', 'name') + " --json"
        VMSSresult = self.utils.shell_execute(commandListVmss)
        jsonVMSSresult = json.loads(VMSSresult[0])
        for indexVMSS in range(len(jsonVMSSresult)):
            commandListVmssvm = "azure vmssvm list -g " + self.config.get('Group', 'name') + " -n " + jsonVMSSresult[indexVMSS]['name'] + " --json"
            VMSSvmresult = self.utils.shell_execute(commandListVmssvm)
            jsonVMSSvmresult = json.loads(VMSSvmresult[0])
            for indexVMSSVM in range(len(jsonVMSSvmresult)):
                self.logger.info("Shuting down : " + jsonVMSSresult[indexVMSS]['name'] + " instance : " + jsonVMSSvmresult[indexVMSSVM]['instanceId'])
                commandShutVmss = "azure vmssvm deallocate -g " + self.config.get('Group', 'name') + " -n " + jsonVMSSresult[indexVMSS]['name'] + " -d " + str(jsonVMSSvmresult[indexVMSSVM]['instanceId'])
                self.utils.shell_execute(commandShutVmss)

    def connect(self):
        """Open an SSH tunnel to the management endpoint, if one doesn't
        already exist. The PID for the tunnel is written to
        `~/.acs/ssh.pid`.  If a tunnel already exiss then a new one will
        not be created instead PID for the existing tunnel will be
        returned.

        This method attempts to block until we have an active connection
        to the master endpoint.

        """
        if not self.exists():
            raise RuntimeError("The service does not exist, create it with `acs service create`.")

        pidpath = os.path.expanduser("~/.acs/ssh.pid")
        if os.path.isfile(pidpath):
            pidfile = open(pidpath)
            pid = pidfile.read()
            pidfile.close()

            # check the process exists
            # 'kill(pid, 0)' does not kill the process, it just throws an `OSError` if the PID does not exist
            try:
                os.kill(int(pid), 0)
                return "A tunnel already exists using PID " + str(pid)
            except OSError:
                # seems the old tunnel has gone away
                self.logger.info("A PIDFile exists, but the process does not seem to be present. Removing the PIDFile and opening a new tunnel.")
                os.remove(pidpath)
    
        try:
            pid = os.fork()
            if pid > 0:
                # Exit parent process
                pidfile = open(pidpath, 'w')
                pidfile.write(str(pid))
                pidfile.close()

                time.sleep(0.5)

                # wait until we can connect to the master endpoint
                isConnected = False
                attempts = 0
                while not isConnected and attempts < 50:
                    req = urllib.request.Request("http://localhost")
                    try:
                        with urllib.request.urlopen(req) as response:
                            html = response.read()
                            isConnected = True
                    except urllib.error.URLError as e:
                        isConnected = False
                        attempts = attempts + 1
                        self.logger.debug("SSH tunnel not established, waiting for 1/10th of a second")
                        time.sleep(0.1)
                        
                if attempts < 50:
                    msg = "Connection opened (PID " + str(pid) + ")"
                else:
                    raise RuntimeError("Unable to open an SSH tunnel to the management endpoint.")
          
                return msg
        except OSError as e:
            msg = "Unable to create forked proces for the SSH Tunnel: " + str(e)
            self.logger.error(msg)
            raise RuntimeError(msg)

        # Decouple from the parent environment
        os.chdir("/")
        os.setsid()
        os.umask(0)

        try:
            with SSHTunnelForwarder(
                    (self.getManagementEndpoint(), 2200),
                    remote_bind_address = ('localhost', 80),
                    local_bind_address = ('', 80),
                    ssh_username = self.config.get('ACS', 'username'),
                    ssh_pkey = os.path.expanduser(self.config.get('SSH', "privatekey"))
            ) as server:
                while True:
                    sleep(10)
        except Exception as e:
            self.logger.error("Unable to open SSH connection:\n" + str(e))
            raise e

    def disconnect(self):
        """
        Close the SSH tunnel to the management endpoint with the supplied pid
        """

        pidpath = os.path.expanduser("~/.acs/ssh.pid")
        if os.path.isfile(pidpath):
            pidfile = open(pidpath)
            pid = pidfile.read()
            pidfile.close()

            # check the process exists
            # 'kill(pid, 0)' does not kill the process, it just throws an `OSError` if the PID does not exist
            try:
                os.kill(int(pid), 0)
            except OSError:
                # seems the old tunnel has gone away
                self.logger.debug("A PIDFile exists, but the process does not seem to be present. Removing the PIDFile.")
                os.remove(pidpath)
        else:
            raise RuntimeWarning("No SSH PID file, therefore assuming there is no active tunnel to close.")

        self.logger.info("Attempting to kill the SSH tunnel, process: " + pid)
        try:
            os.kill(int(pid), signal.SIGTERM)
            time.sleep(1.0)
            os.remove(pidpath)
            return "Disconnected"
        except OSError as err:
            self.logger.exception(err)
            raise RuntimeError("Unable to killthe SSH Tunnel process: " + str(err))


    def executeOnMaster(self, cmd):
        """
        Execute command on the current master leader
        """
        if self._hostnameResolves(self.getManagementEndpoint()):
            ssh = SSHClient()
            ssh.load_system_host_keys()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(
                self.getManagementEndpoint(),
                username = self.config.get('ACS', "username"),
                port = 2200,
                key_filename = os.path.expanduser(self.config.get('SSH', "privatekey")))
            session = ssh.get_transport().open_session()
            self.logger.debug("Session opened on master.")
            self.logger.debug("Executing on master: " + cmd)

            AgentRequestHandler(session)
            stdin, stdout, stderr = ssh.exec_command(cmd)
            stdin.close()
      
            result = ""
            for line in stdout.read().splitlines():
                self.logger.debug(line.decude("utf-8"))
                result = result + line.decode("utf-8") + "\n"
            for line in stderr.read().splitlines():
                self.logger.error(line.decode("utf-8"))
        else:
            self.logger.error("Endpoint " + self.getManagementEndpoint() + " does not exist, cannot SSH into it.")
            result = "Exception: No cluster is available at " + self.getManagementEndpoint()
        ssh.close()
        return result

    def getManagementEndpoint(self):
        return self.config.get('ACS', 'dnsPrefix') + 'mgmt.' + self.config.get('Group', 'region').replace(" ", "").replace('"', '') + '.cloudapp.azure.com'

    def getAgentEndpoint(self):
        return self.config.get('ACS', 'dnsPrefix') + 'agents.' + self.config.get('Group', 'region').replace(" ", "").replace('"', '') + '.cloudapp.azure.com'

    def createResourceGroup(self):
        self.logger.debug("Creating Resource Group")

        command = "azure group create " + self.config.get('Group', 'name')  + " " + self.config.get('Group', 'region')
        os.system(command)

    def executeOnAgent(self, cmd, ip):
        """Execute command on an agent identified by agent_name

        """
        sshadd = "ssh-add " + self.config.get("SSH", "privatekey")
        self.utils.shell_execute(sshadd)
    
        sshAgentConnection = "ssh -o StrictHostKeyChecking=no " + self.config.get('ACS', 'username') + '@' + ip
        self.logger.debug("SSH Connection to agent: " + sshAgentConnection)
    
        self.logger.debug("Command to run on agent: " + cmd)
    
        sshCmd = sshAgentConnection + ' \'' + cmd + '\''
        self.utils.shell_execute("exit")
        result = self.executeOnMaster(sshCmd)

        return result

    def getClusterSetup(self):
        """Get all the data about how this cluster is configured.

        """
        data = {}
        data["parameters"] = self.config.getACSParams()
    
        fqdn = {}
        fqdn["master"] = self.getManagementEndpoint()
        fqdn["agent"] = self.getAgentEndpoint()
        data["domains"] = fqdn
        
        data["sshTunnel"] = "ssh -o StrictHostKeyChecking=no -L 80:localhost:80 -N " + self.config.get('ACS', 'username') + "@" + self.getManagementEndpoint() + " -p 2200"

        azure = {}
        azure['resourceGroup'] = self.config.get('Group', 'name')
        data["azure"] = azure

        return data

    def _hostnameResolves(self, hostname):
        try:
            socket.gethostbyname(hostname)
            return True
        except socket.error:
            return False

    def getAgentIPs(self):
        ### Return a list of Agent IPs in this cluster. ###
    
        agentPool = AgentPool(self.config)
        nics = agentPool.getNICs()
        
        ips = []
        for nic in nics:
            try:
                ip = nic["ipConfigurations"][0]["privateIPAddress"]
                self.logger.debug("IP for " + nic["name"] + " is: " + str(ip))
                ips.append(ip)
            except KeyError:
                self.logger.warning("NIC doesn't seem to have the information we need")
        
        self.logger.debug("Agent IPs: " + str(ips))
        return ips

"""The cofiguration for an ACS cluster to work with"""

import configparser
import os 

class Config(object):

  def __init__(self, filename):

    if not filename:
      filename = "~/.acs/default.ini"

    self.filename = os.path.expanduser(filename)

    if not os.path.isfile(self.filename):
      dns = input("What is the DNS prefix for this cluster?\n")
      group = input("What is the name of the resource group you want to use/create?\n")
      region = input("In which region do you want to deploy the resource group (default: westus)?\n") or 'westus'
      username = input("What is your username (default: azureuser)?\n") or 'azureuser'
      orchestrator = input("Which orchestrator do you want to use (Swarm or DCOS, default: DCOS)?\n") or 'DCOS'
      masterCount = input("How many masters do you want in your cluster (1, 3 or 5, default: 3)?\n") or '3'
      agentCount = input("How many agents do you want in your cluster (default: 3)?\n") or '3'
      agentSize = input("Agent size required (default: Standard_D2_v2)?\n") or 'Standard_D2_v2'
      
      tmpl = open("config/cluster.ini.tmpl")
      output = open(self.filename, 'w')
      for s in tmpl:
        s = s.replace("MY-DNS-PREFIX", dns)
        s = s.replace("MY-RESOURCE-REGION", region)
        s = s.replace("MY-RESOURCE-GROUP-NAME", group)
        s = s.replace("MY-USERNAME", username)
        s = s.replace("MY-ORCHESTRATOR", orchestrator)
        s = s.replace("MY-MASTER-COUNT", masterCount)
        s = s.replace("MY-AGENT-COUNT", agentCount)
        s = s.replace("MY-AGENT-SIZE", agentSize)
        output.write(s)

      tmpl.close()
      output.close()

    defaults = {"orchestratorType": "DCOS"}
    config = configparser.ConfigParser(defaults)
    config.read(self.filename)
    config.set('Group', 'name', config.get('Group', 'name'))
    self.config_parser = config
      
  def get(self, section, name):
    value = self.config_parser.get(section, name)

    if section == "SSH": 
      public_filepath = os.path.expanduser(self.config_parser.get('SSH', 'publicKey'))
      private_filepath = os.path.expanduser(self.config_parser.get('SSH', 'privatekey'))

      if name == "privateKey":
        if not os.path.isfile(private_filepath):
          self._generateSSHKey(private_filepath, public_filepath)
        with open(private_filepath, 'r') as sshfile: 
          value = sshfile.read().replace('\n', '') 
      elif name == "publickey":
        if not os.path.isfile(public_filepath):
          self._generateSSHKey(private_filepath, public_filepath)
        with open(public_filepath, 'r') as sshfile: 
          value = sshfile.read().replace('\n', '') 
        
    return value

  def getint(self, section, name):
    return self.config_parser.getint(section, name)

  def value(self, set_to):
    value = {}
    value["value"] = set_to
    return value
    
  def getACSParams(self):
    """
    Get a dictionary of all ACS parameters. Note that 
    this is not all the parameters provided in the config 
    file, only the ones needed by the ACS Resource Provider'
    """
    params = {}
    params["dnsNamePrefix"] = self.value(self.get('ACS', 'dnsPrefix'))
    params["orchestratorType"] = self.value(self.get('ACS', 'orchestratorType'))
    params["agentCount"] = self.value(self.getint('ACS', 'agentCount'))
    params["agentVMSize"] = self.value(self.get('ACS', 'agentVMSize'))
    params["masterCount"] = self.value(self.getint('ACS', 'masterCount'))
    params["linuxAdminUsername"] = self.value(self.get('ACS', 'username'))
    params["sshRSAPublicKey"] = self.value(self.get('SSH', 'publickey'))
  
    return params

  def _generateSSHKey(self, private_filepath, public_filepath):
    """
    Generate public and private keys. The filepath parameters 
    are the paths top the respective publoic and private key files.
    """
    (ssh_dir, filename) = os.path.split(os.path.expanduser(private_filepath))
    if not os.path.exists(ssh_dir):
      os.makedirs(ssh_dir)

    key = paramiko.RSAKey.generate(1024)
    key.write_private_key_file(os.path.expanduser(private_filepath))
    
    with open(os.path.expanduser(public_filepath),"w") as public:
      public.write("%s %s"  % (key.get_name(), key.get_base64()))

    public.close()
