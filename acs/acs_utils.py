#!/usr/bin/python

from .AgentPool import *
from .ACSLogs import *
from .commands.afs import *

import ConfigParser
import json
import os
from os.path import expanduser
import paramiko
from paramiko import SSHClient
from scp import SCPClient
import subprocess

class ACSUtils:
    def __init__(self, configfile = "cluster.ini"):
        self.log = ACSLog("ACSUtils")
        self.log.debug("Reading config from " + configfile)
        defaults = {"orchestratorType": "Mesos"}
        config = ConfigParser.ConfigParser(defaults)
        config.read(configfile)
        config.set('Group', 'name', config.get('ACS', 'dnsPrefix'))
        self.config = config
        
        #self.ssh = SSHClient()
        #self.ssh.load_system_host_keys()
        #self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        #self.ssh.connect(self.getManagementEndpoint(), username = self.config.get('ACS', "username"), port=2200)
        #self._configureSSH()

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



    def scale(self, capacity):
        """
        Scale the number of Agents availalbe to the supplied number
        """
        agentPool = AgentPool(self.config)
        agentPool.scale(capacity)

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

    def getMasterSSHConnection(self):
        url = self.getManagementEndpoint()
        return "ssh -o StrictHostKeyChecking=no " + self.config.get('ACS', 'username') + '@' + url + ' -p 2200'

    def _configureSSH(self):
        """Configure SSH on the master so that it can connect to the agents"""
        home = expanduser("~")
        localfile = home + "/.ssh/id_rsa"
        remotefile = "~/.ssh/id_rsa"
        with SCPClient(self.ssh.get_transport()) as scp:
            scp.put(localfile, remotefile)


    def agentDockerCommand(self, docker_cmd):
        """ Run a Docker command on each of the agents """
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
                afs.addTo(self)
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
        hosts = self.getAgentHostNames()
        for host in hosts:
            cmd = "wget https://github.com/Microsoft/OMS-Agent-for-Linux/releases/download/v1.1.0-28/omsagent-1.1.0-28.universal.x64.sh\n"
            self.executeOnAgent(cmd, host)

            cmd = "chmod +x ./omsagent-1.1.0-28.universal.x64.sh\n"
            self.executeOnAgent(cmd, host)

            workspace_id = self.config.get('OMS', "workspace_id")
            workspace_key = self.config.get('OMS', "workspace_primary_key")
            cmd = "sudo ./omsagent-1.1.0-28.universal.x64.sh --upgrade -w " + workspace_id + " -s " + workspace_key + "\n"
            self.executeOnAgent(cmd, host)

            cmd = "sudo sed -i -E \"s/(DOCKER_OPTS=\\\")(.*)\\\"/\\1\\2 --log-driver=fluentd --log-opt fluentd-address=localhost:25225\\\"/g\" /etc/default/docker\n"
            self.executeOnAgent(cmd, host)

            cmd = "sudo service docker restart\n"
            self.executeOnAgent(cmd, host)

