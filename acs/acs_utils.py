#!/usr/bin/python

from AgentPool import *
from ACSLogs import *

import ConfigParser
import json
import os
import paramiko
import subprocess

class ACSUtils:
    def __init__(self, configfile = "cluster.ini"):
        self.log = ACSLog()
        self.log.debug("Reading config from " + configfile)
        defaults = {"orchestratorType": "Mesos"}
        config = ConfigParser.ConfigParser(defaults)
        config.read(configfile)
        config.set('Group', 'name', config.get('ACS', 'dnsPrefix'))
        self.config = config

    def value(self, set_to):
        value = {}
        value["value"] = set_to
        return value

    def getACSParams(self):
        params = {}
        params["dnsNamePrefix"] = self.value(self.config.get('ACS', 'dnsPrefix'))
        params["orchestratorType"] = self.value(self.config.get('ACS', 'orchestratorType'))
        params["agentCount"] = self.value(self.config.getint('ACS', 'agentCount'))
        params["agentVMSize"] = self.value(self.config.get('ACS', 'agentVMSize'))
        params["masterCount"] = self.value(self.config.getint('ACS', 'masterCount'))
        params["sshRSAPublicKey"] = self.value(self.config.get('ACS', 'sshPublicKey'))
        return params

    def getEnvironmentSettings(self):
        """
        Return a dictionary of usefel information about the ACS configuration.
        """
        out = {}
        
        out["orchestratorType"] = self.getMode()
        if self.getMode() == "SwarmPreview":
            sshTunnel = "ssh -L 2375:localhost:2375 -N " + self.config.get('ACS', 'username') + '@' + self.getManagementEndpoint() + " -p 2200"
        elif self.getMode() == "Mesos":
            sshTunnel = "ssh -L 80:localhost:80 -N " + self.config.get('ACS', 'username') + '@' + self.getManagementEndpoint() + " -p 2200"
        else:
            sshTunnel = "(Need to add support to CLI to generate tunnel info for this orchestrator type)"
        out["sshTunnel"] = sshTunnel
        
        public = self.config.get('ACS', 'dnsPrefix') + 'agents.' + self.config.get('Group', 'region').replace(" ", "").replace('"', '') + '.cloudapp.azure.com'
        out["publicFQDN"] = public

        return out

    def getMode(self):
        """Get the orchestrator mode for this instance of ACS"""
        return self.config.get("ACS", "orchestratorType")

    def createResourceGroup(self):
        command = "azure group create " + self.config.get('Group', 'name')  + " " + self.config.get('Group', 'region')
        os.system(command)

    def deleteResourceGroup(self):
        command = "azure group delete " + self.config.get('Group', 'name')
        self.log.info("Command: " + command)
        os.system(command)

    def createDeployment(self):
        self.log.debug("Creating Deployment")
        self.log.debug(json.dumps(self.getACSParams()))
        self.createResourceGroup()

        command = "azure group deployment create"
        command = command + " " + self.config.get('ACS', 'dnsPrefix')
        command = command + " " + self.config.get('ACS', 'dnsPrefix')
        command = command + " --template-uri " + self.config.get('Template', 'templateUrl')
        command = command + " -p '" + json.dumps(self.getACSParams()) + "'"
    
        os.system(command)

    def createStorage(self):
        self.log.debug("Creating Storage Account")
        self.createResourceGroup()
    
        command = "azure storage account create"
        command = command + " --type " + self.config.get('Storage', 'type')
        command = command + " --resource-group " + self.config.get('Group', 'name')
        command = command + " --location " + self.config.get('Group', 'region')
        command = command + " " + self.config.get('Storage', 'name')
    
        os.system(command)

        key = self.getStorageAccountKey()

        try:
            command = "azure storage share create"
            command = command + " --account-name " + self.config.get('Storage', 'name')
            command = command + " --account-key " + key
            command = command + " " + self.config.get('Storage', 'shareName')

            out = subprocess.check_output(command, shell=True)
        except:
            # FIXME: test if the share already exists, if it does then don't try to recreate it
            # For now we just assume that an error is always that the share alrady exists 
            self.log.warning("Failed to create share, assuming it is because it already exists")

    def getStorageAccountKey(self):
        command = "azure storage account keys list"
        command = command + " --resource-group " + self.config.get('Group', 'name')
        command = command + " " + self.config.get('Storage', 'name')
        command = command + " --json"

        keys = json.loads(subprocess.check_output(command, shell=True))
        return keys['storageAccountKeys']['key1']

    def getShareEndpoint(self):
        command = "azure storage account show"
        command = command + " --resource-group " + self.config.get('Group', 'name')
        command = command + " " + self.config.get('Storage', 'name')
        command = command + " --json"
        
        data = json.loads(subprocess.check_output(command, shell=True))
        endpoint = data['primaryEndpoints']['file']

        return endpoint

    def scale(self, capacity):
        """
        Scale the number of Agents availalbe to the supplied number
        """
        agentPool = AgentPool(self.config)
        agentPool.scale(capacity)

    def getManagementEndpoint(self):
        return self.config.get('ACS', 'dnsPrefix') + 'mgmt.' + self.config.get('Group', 'region').replace(" ", "").replace('"', '') + '.cloudapp.azure.com'

    def marathonCommand(self, command, method = 'GET', data = None):
        curl = 'curl -s -X ' + method 
        if data != None:
            curl = curl + " -d \"" + data + "\" -H \"Content-type:application/json\""
        cmd = curl + ' localhost:8080/v2/' + command 
        self.log.debug('Command to execute: ' + cmd)
        return subprocess.check_output(cmd, shell=True)

    def dockerCommand(self, command):
        url = self.getManagementEndpoint()
        cmd = 'docker ' + command

        self.log.debug('Command to execute: ' + cmd)
        return subprocess.check_output(cmd, env={'DOCKER_HOST': ':2375'}, shell=True)

    def composeCommand(self, command, file = 'docker-compose.yml', options = ''):
        url = self.getManagementEndpoint()
        cmd = 'docker-compose -f ' + file + ' ' + command + ' ' + options

        self.log.debug('Command to execute: ' + cmd)
        return subprocess.check_output(cmd, env={'DOCKER_HOST': ':2375'}, shell=True)

    def openSwarmTunnel(self):
        url = self.getManagementEndpoint()
        cmd = 'ssh -L 2375:localhost:2375 -N ' + self.config.get('ACS', 'username') + '@' + url + ' -p 2200'
        return "If you get errors ensure that you have craeted an SSH tunnel to your master by running '" + cmd + "'"

    def openMesosTunnel(self):
        url = self.getManagementEndpoint()
        cmd = 'ssh -L 8080:localhost:8080 -N ' + self.config.get('ACS', 'username') + '@' + url + ' -p 2200'
        return "If you get errors eIn order to manage your cluster you need to open an SSH tunnel to it using the command  '" + cmd + "'"

    def getAgentsFQDN(self):
        return self.config.get('ACS', 'dnsPrefix') + 'agents.' + self.config.get('Group', 'region') + '.cloudapp.azure.com'

    def getAgentHostNames(self):
        # return a list of Agent Host Names in this cluster
        
        agentPool = AgentPool(self.config)
        agents = agentPool.getAgents()

        names = []
        for agent in agents:
            name = agent['properties']['osProfile']['computerName']
            if "-agent-" in name:
                names.append(name)
        return names

    def getMasterSSHConnection(self):
        url = self.getManagementEndpoint()
        return "ssh -o StrictHostKeyChecking=no " + self.config.get('ACS', 'username') + '@' + url + ' -p 2200'

    def configureSSH(self):
        """Configure SSH on the master so that it can connect to the agents"""
        self.log.warning("Currently configure SSH on every call, this is wasteful, should maintain state of machines and only configure once")

        cmd = self.getMasterSSHConnection() + " " + "echo Hello Master"
        self.log.debug("Making an SSH call to verify all is OK: " + cmd)
        subprocess.check_output(cmd, shell=True)

        url = self.getManagementEndpoint()
        conn = "scp -P 2200 -o StrictHostKeyChecking=no"
        localfile = "~/.ssh/id_rsa"
        remotefile = self.config.get('ACS', 'username') + '@' + url + ":~/.ssh/id_rsa"
    
        cmd = conn + " " + localfile + " " + remotefile
        self.log.debug("SCP command: " + cmd)

        out = subprocess.check_output(cmd, shell=True)

    def executeOnMaster(self, cmd):
        """
OA        Execute command on the current master leader
        """
        sshMasterConnection = self.getMasterSSHConnection()
        self.log.debug("SSH Master Connection: " + sshMasterConnection)

        sshCmd = sshMasterConnection + ' "' + cmd + '"'
        self.log.info("Command to run on client: " + sshCmd)
        out = subprocess.check_output(sshCmd, shell=True)
        self.log.debug("Output:\n" + out)


    def executeOnAgent(self, cmd, agent_name):
        """
        Execute command on an agent identified by agent_name
        """
        sshAgentConnection = "ssh -o StrictHostKeyChecking=no " + self.config.get('ACS', 'username') + '@' + agent_name
        self.log.debug("SSH Connection to agent: " + sshAgentConnection)

        self.log.debug("Command to run on agent: " + cmd)

        cmd = cmd.replace("\"", "\\\"")
        sshCmd = sshAgentConnection + ' \'' + cmd + '\''
        self.log.info("Command to run on master: " + sshCmd)
        self.executeOnMaster(sshCmd)

    def agentDockerCommand(self, docker_cmd):
        """ Run a Docker command on each of the agents """
        self.configureSSH()

        hosts = self.getAgentHostNames()
        for host in hosts:
            self.executeOnAgent("docker " + docker_cmd, host)

    def addFeatures(self, features = None):
        """Add all features specified in the config file or the features
        parameter (as a comma separated list) to this cluster. """
        if (features == None):
            features = self.config.get('Features', "featureList")
        if features == "":
            self.log.info("No features to add")
        else:
            self.log.info("Adding features to ACS: " + features)

        featureList = [x.strip() for x in features.split(',')]
        for feature in featureList:
            self.log.debug("Adding feature: " + feature)
            hosts = self.getAgentHostNames()
            if feature == "afs":
                self.createStorage()
                self.configureSSH()
                hosts = self.getAgentHostNames()
                self.addAzureFileService(hosts)
            elif feature == "oms":
                self.addOMS()
            elif feature[:5] == "pull ":
                print("'addFeature pull' is deprecated. Please use 'docker pull' instead")
                self.agentDockerCommand(feature)
            else:
                self.log.error("Unknown feature: " + feature)

    def addOMS(self):
        """
        Add OMS to all Agents using the details defined in the config
        file (OMS_WORKSPACE_ID and OMS_WORKSPACE_PRIMARY_KEY).
        """
        self.configureSSH()

        f = open('installOMS.sh', 'w')
        f.write("wget https://github.com/Microsoft/OMS-Agent-for-Linux/releases/download/v1.1.0-28/omsagent-1.1.0-28.universal.x64.sh\n")
        f.write("chmod +x ./omsagent-1.1.0-28.universal.x64.sh\n")
        workspace_id = self.config.get('OMS', "workspace_id")
        workspace_key = self.config.get('OMS', "workspace_primary_key")
        f.write("sudo ./omsagent-1.1.0-28.universal.x64.sh --upgrade -w " + workspace_id + " -s " + workspace_key + "\n")
        f.write("sudo sed -i -E \"s/(DOCKER_OPTS=\\\")(.*)\\\"/\\1\\2 --log-driver=fluentd --log-opt fluentd-address=localhost:25225\\\"/g\" /etc/default/docker\n")
        f.write("sudo service docker restart\n")
        f.close()

        url = self.getManagementEndpoint()
        conn = "scp -P 2200 -o StrictHostKeyChecking=no"
        localfile = "installOMS.sh"
        remotefile = self.config.get('ACS', 'username') + '@' + url + ":~/installOMS.sh"
        cmd = conn + " " + localfile + " " + remotefile
        self.log.debug("SCP command to copy install script to master: " + cmd)
        out = subprocess.check_output(cmd, shell=True)

        hosts = self.getAgentHostNames()
        for host in hosts:
            self.log.debug("Installing OMS on: " + host)
            conn = "scp -o StrictHostKeyChecking=no"
            localfile = "installOMS.sh"
            remotefile = self.config.get('ACS', 'username') + '@' + host + ":~/installOMS.sh"
            cmd = conn + " " + localfile + " " + remotefile
            self.log.debug("SCP command to copy install script to agent: " + cmd)
            self.executeOnMaster(cmd)

            sshCommand = "chmod 755 ~/installOMS.sh"
            self.executeOnAgent(sshCommand, host)

            sshCommand = "sudo ./installOMS.sh"
            self.executeOnAgent(sshCommand, host)

    def addAzureFileService(self, hosts):
        # Add an Azure File Service to identified agents
        url = self.getManagementEndpoint()
        package = "cifs-utils"

        sshMasterConnection = self.getMasterSSHConnection()
        self.log.debug("SSH Master Connection: " + sshMasterConnection)

        for host in hosts:
            sshCommand = "mkdir -p " + mount
            self.executeOnAgent(sshCommand, host)

            urn = self.getShareEndpoint().replace("https:", "") + self.config.get("Storage", "shareName")
            username = self.config.get("Storage", "name")
            password = self.getStorageAccountKey()
            sshCommand = "sudo mount -t cifs " + urn + " " + mount + " -o uid=1000,gid=1000,vers=2.1,username=" + username + ",password=" + password
            self.executeOnAgent(sshCommand, host)
