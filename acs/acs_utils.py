#!/usr/bin/python

import ConfigParser
import json
import logging
import os
import paramiko
import subprocess

class ACSLog:
    def __init__(self, name = "acs"):
        output_dir = 'logs'
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        if (not self.logger.handlers):
            # create console handler and set level to info
            handler = logging.StreamHandler()
            handler.setLevel(logging.DEBUG)
            formatter = logging.Formatter("%(levelname)s - %(message)s")
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            
            # create error file handler and set level to error
            handler = logging.FileHandler(os.path.join(output_dir, "error.log"),"w", encoding=None, delay="true")
            handler.setLevel(logging.ERROR)
            formatter = logging.Formatter("%(levelname)s - %(message)s")
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            
            # create debug file handler and set level to debug
            handler = logging.FileHandler(os.path.join(output_dir, "all.log"),"w")
            handler.setLevel(logging.DEBUG)
            formatter = logging.Formatter("%(levelname)s - %(message)s")
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def info(self, msg):
        self.logger.info(msg)

    def debug(self, msg):
        self.logger.debug(msg)

    def warning(self, msg):
        self.logger.warning(msg)

    def error(self, msg):
        self.logger.error(msg)

class ACSUtils:
    def __init__(self, configfile = "cluster.ini"):
        self.log = ACSLog()
        self.log.debug("Reading config from " + configfile)
        defaults = {"orchestratorType": "Mesos", "jumpboxOS": "Linux"}
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
        params["agentCount"] = self.value(self.config.getint('ACS', 'agentCount'))
        params["agentVMSize"] = self.value(self.config.get('ACS', 'agentVMSize'))
        params["masterCount"] = self.value(self.config.getint('ACS', 'masterCount'))
        params["sshRSAPublicKey"] = self.value(self.config.get('ACS', 'sshPublicKey'))
        return params

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
    
        cmd = "azure resource list -r Microsoft.Compute/virtualMachines " + self.config.get('Group', 'name') +  " --json"
        self.log.debug("Execute command: " + cmd)

        agents = json.loads(subprocess.check_output(cmd, shell=True))
        names = []
        for agent in agents:
            name = agent['name']
            if "-agent-" in name:
                names.append(name)
        return names

    def getMasterSSHConnection(self):
        url = self.getManagementEndpoint()
        return "ssh -o StrictHostKeyChecking=no -o StrictHostKeyChecking=no " + self.config.get('ACS', 'username') + '@' + url + ' -p 2200'

    def configureSSH(self):
        """Configure SSH on the master so that it can connect to the agents"""
        cmd = self.getMasterSSHConnection() + " " + "echo Hello Master"
        self.log.debug("Making an SSH call to verify all is OK: " + cmd)
        subprocess.check_output(cmd, shell=True)

        url = self.getManagementEndpoint()
        conn = "scp -P 2200"
        localfile = "~/.ssh/id_rsa"
        remotefile = self.config.get('ACS', 'username') + '@' + url + ":~/.ssh/id_rsa"
    
        cmd = conn + " " + localfile + " " + remotefile
        self.log.debug("SCP command: " + cmd)

        out = subprocess.check_output(cmd, shell=True)

    def agentDockerCommand(self, docker_cmd):
        """ Run a Docker command on each of the agents """
        url = self.getManagementEndpoint()

        sshMasterConnection = self.getMasterSSHConnection()
        self.log.debug("SSH Master Connection: " + sshMasterConnection)

        hosts = self.getAgentHostNames()
        for host in hosts:
            sshAgentConnection = "ssh -o StrictHostKeyChecking=no " + self.config.get('ACS', 'username') + '@' + host
            self.log.debug("SSH Agent Connection: " + sshAgentConnection)

            sshCommand = "docker " + docker_cmd
            self.log.debug("Command to run: " + sshCommand)
        
            cmd = sshMasterConnection + ' "' + sshAgentConnection + ' \'' + sshCommand + '\'"'
            out = subprocess.check_output(cmd, shell=True)
            self.log.debug("Output:\n" + out)        

    def addFeatures(self, features = None):
        """Add all fetures specified in the config file or the features
        parameter (as a comma separated list) to this cluster. """
        if (features == None):
            features = self.config.get('Features', "featureList")
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
            elif feature[:5] == "pull ":
                print("'addFeature pull' is deprecated. Please use 'docker pull' instead")
                self.agentDockerCommand(feature)
            else:
                self.log.error("Unknown feature: " + feature)

    def addAzureFileService(self, hosts):
        # Add an Azure File Service to identified agents
        url = self.getManagementEndpoint()
        package = "cifs-utils"

        sshMasterConnection = self.getMasterSSHConnection()
        self.log.debug("SSH Master Connection: " + sshMasterConnection)

        for host in hosts:
            sshAgentConnection = "ssh -o StrictHostKeyChecking=no " + self.config.get('ACS', 'username') + '@' + host
            self.log.debug("SSH Agent Connection: " + sshAgentConnection)

            mount = self.config.get("Storage", "mount")
            sshCommand = "mkdir -p " + mount
            self.log.debug("Command to run: " + sshCommand)
        
            cmd = sshMasterConnection + ' "' + sshAgentConnection + ' \'' + sshCommand + '\'"'
            out = subprocess.check_output(cmd, shell=True)
            self.log.debug("Output:\n" + out)

            urn = self.getShareEndpoint().replace("https:", "") + self.config.get("Storage", "shareName")
            username = self.config.get("Storage", "name")
            password = self.getStorageAccountKey()
            sshCommand = "sudo mount -t cifs " + urn + " " + mount + " -o uid=1000,gid=1000,vers=2.1,username=" + username + ",password=" + password
            self.log.debug("Command to run: " + sshCommand)
            cmd = sshMasterConnection + ' "' + sshAgentConnection + ' \'' + sshCommand + '\'"'
            out = subprocess.check_output(cmd, shell=True)
            self.log.debug("Output:\n" + out)
        
