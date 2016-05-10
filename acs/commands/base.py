"""The base command class. All implemented commands should extend this class."""
from ..AgentPool import AgentPool

from sshtunnel import SSHTunnelForwarder
import json
import os.path
import paramiko
from paramiko import SSHClient
from paramiko.agent import AgentRequestHandler
from time import sleep
import socket
import subprocess

class Base(object):

  def __init__(self, config, options, *args, **kwargs):
    self.log = ACSLog("Base")
    self.config = config
    self.options = options
    self.args = args
    self.kwargs = kwargs

  def _hostnameResolves(self, hostname):
    try:
      socket.gethostbyname(hostname)
      return True
    except socket.error:
      return False

  def getManagementEndpoint(self):
    return self.config.get('ACS', 'dnsPrefix') + 'mgmt.' + self.config.get('Group', 'region').replace(" ", "").replace('"', '') + '.cloudapp.azure.com'

  def getAgentEndpoint(self):
    return self.config.get('ACS', 'dnsPrefix') + 'agents.' + self.config.get('Group', 'region').replace(" ", "").replace('"', '') + '.cloudapp.azure.com'

  def createResourceGroup(self):
    self.log.debug("Creating Resource Group")

    command = "azure group create " + self.config.get('Group', 'name')  + " " + self.config.get('Group', 'region')
    os.system(command)

  def run(self):
    raise NotImplementedError("You must implement the run() method in your commands")

  def help(self):
    raise NotImplementedError("You must implement the help method. In most cases you will simply do 'print(__doc__)'")

  def getAgentIPs(self):
    # return a list of Agent IPs in this cluster
    
    agentPool = AgentPool(self.config)
    nics = agentPool.getNICs()
    
    ips = []
    for nic in nics:
      self.log.debug("Extracting IP from: " + json.dumps(nic, indent=True))
      ip = nic["properties"]["ipConfigurations"][0]["properties"]["privateIPAddress"]
      self.log.debug("IP is: " + str(ip))
      ips.append(ip)

    return ips

  def executeOnAgent(self, cmd, ip):
    """
    Execute command on an agent identified by agent_name
    """
    sshAgentConnection = "ssh -o StrictHostKeyChecking=no " + self.config.get('ACS', 'username') + '@' + ip
    self.log.debug("SSH Connection to agent: " + sshAgentConnection)
    
    self.log.debug("Command to run on agent: " + cmd)
    
    cmd = cmd.replace("\"", "\\\"")
    sshCmd = sshAgentConnection + ' \'' + cmd + '\''
    return self.executeOnMaster(sshCmd)

  def executeOnMaster(self, cmd):
    """
    Execute command on the current master leader
    """
    self.log.debug("Executing on master: " + cmd)

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
      AgentRequestHandler(session)
      stdin, sterr, stdout = ssh.exec_command(cmd)
      stdin.close()
      
      result = ""
      for line in stdout.read().splitlines():
        self.log.debug(line)
        result = result + line
    else:
      self.log.error("Endpoint " + self.getManagementEndpoint() + " does not exist, cannot SSH into it.")
      result = "Exception: No test cluster is available"
    return result

  def sshTunnel(self, command = None):
    """
    Either open an SSH tunnel and keep it open (if command = None) 
    or open the tunnel, execute the command and exit.
    """
    with SSHTunnelForwarder(
      (self.getManagementEndpoint(), 2200),
      remote_bind_address = ('localhost', 80),
      local_bind_address = ('', 80),
      ssh_username = self.config.get('ACS', 'username'),
      ssh_pkey = os.path.expanduser(self.config.get('SSH', "privatekey"))
    ) as server:
      if command:
        return subprocess.check_output(command, shell=True)
      else:
        while True:
          sleep(1)

  def getClusterSetup(self):
    """
    Get all the data about how this cluster is configured.
    """
    data = {}
    data["parameters"] = self.config.getACSParams()
    
    fqdn = {}
    fqdn["master"] = self.getManagementEndpoint()
    fqdn["agent"] = self.getAgentEndpoint()
    data["domains"] = fqdn
  
    return data





"""The cofiguration for an ACS cluster to work with"""
from acs.ACSLogs import ACSLog

import ConfigParser
import os 

class Config(object):

  def __init__(self, filename):
    print("Crete base object")
    self.log = ACSLog("Config")

    self.config_filename = filename
    if not self.config_filename:
      self.config_filename = "cluster.ini"
    if os.path.isfile(self.config_filename):
      self.log.info("Using configuration file : " + self.config_filename)
      defaults = {"orchestratorType": "DCOS"}
      config = ConfigParser.ConfigParser(defaults)
      config.read(self.config_filename)
      config.set('Group', 'name', config.get('ACS', 'dnsPrefix'))
      self.config_parser = config
    else:
      raise Exception("Configuration file '" + self.config_filename + "' not found")

    print("config file: " + self.config_filename)

  def get(self, section, name):
    return self.config_parser.get(section, name)

  def getint(self, section, name):
    return self.config_parser.getint(section, name)

  def value(self, set_to):
    value = {}
    value["value"] = set_to
    return value
    
  def getACSParams(self):
    params = {}
    params["dnsNamePrefix"] = self.value(self.get('ACS', 'dnsPrefix'))
    params["orchestratorType"] = self.value(self.get('ACS', 'orchestratorType'))
    params["agentCount"] = self.value(self.getint('ACS', 'agentCount'))
    params["agentVMSize"] = self.value(self.get('ACS', 'agentVMSize'))
    params["masterCount"] = self.value(self.getint('ACS', 'masterCount'))
    params["sshRSAPublicKey"] = self.value(self.get('SSH', 'publicKey'))
    return params
