#!/usr/bin/python

import ConfigParser
import json
import logging
import os
import subprocess

output_dir = 'logs'
global logger 
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# create console handler and set level to info
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

# create error file handler and set level to error
handler = logging.FileHandler(os.path.join(output_dir, "error.log"),"w", encoding=None, delay="true")
handler.setLevel(logging.ERROR)
formatter = logging.Formatter("%(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

# create debug file handler and set level to debug
handler = logging.FileHandler(os.path.join(output_dir, "all.log"),"w")
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

def getLogger():
    return logger

def value(set_to):
    value = {}
    value["value"] = set_to
    return value

def getConfig(filename = "cluster.ini"):
    logger = getLogger()
    defaults = {"orchestratorType": "Mesos", "jumpboxOS": "Linux"}
    config = ConfigParser.ConfigParser(defaults)
    config.read(filename)
    config.set('Cluster', 'resourceGroup', config.get('Cluster', 'dnsPrefix'))
    return config

def getClusterParams(config):
    params = {}
    params["dnsNamePrefix"] = value(config.get('Cluster', 'dnsPrefix'))
    params["agentCount"] = value(config.getint('Cluster', 'agentCount'))
    params["agentVMSize"] = value(config.get('Cluster', 'agentVMSize'))
    params["masterCount"] = value(config.getint('Cluster', 'masterCount'))
    params["sshRSAPublicKey"] = value(config.get('Cluster', 'sshPublicKey'))
    if config.get('Cluster', 'orchestratorType') == 'mesos':
        params["adminPassword"] = value(config.get('Cluster', 'password'))
    return params

def createResourceGroup(config):
    command = "azure group create " + config.get('Cluster', 'resourceGroup')  + " " + config.get('Cluster', 'region')
    os.system(command)

def deleteResourceGroup(config):
    command = "azure group delete " + config.get('Cluster', 'resourceGroup')
    os.system(command)

def createDeployment(config):
    logger = getLogger()
    logger.debug("Creating Deployment")
    logger.debug(json.dumps(getClusterParams(config)))
    createResourceGroup(config)

    command = "azure group deployment create"
    command = command + " " + config.get('Cluster', 'dnsPrefix')
    command = command + " " + config.get('Cluster', 'dnsPrefix')
    command = command + " --template-uri " + config.get('Template', 'templateUrl')
    command = command + " -p '" + json.dumps(getClusterParams(config)) + "'"
    
    os.system(command)

def getManagementEndpoint(config):
    return config.get('Cluster', 'dnsPrefix') + 'mgmt.' + config.get('Cluster', 'region').replace(" ", "").replace('"', '') + '.cloudapp.azure.com'

def marathonCommand(config, command, method = 'GET', data = None):
    logger = getLogger()
    curl = 'curl -s -X ' + method 
    if data != None:
        curl = curl + " -d \"" + data + "\" -H \"Content-type:application/json\""
    cmd = curl + ' localhost:8080/v2/' + command
    logger.debug('Command to execute: ' + cmd)
    return subprocess.check_output(cmd, shell=True)

def dockerCommand(config, command):
    url = getManagementEndpoint(config)
    cmd = 'docker ' + command

    logger.debug('Command to execute: ' + cmd)
    return subprocess.check_output(cmd, env={'DOCKER_HOST': ':2375'}, shell=True)

def composeCommand(config, command, file = 'docker-compose.yml', options = ''):
    url = getManagementEndpoint(config)
    cmd = 'docker-compose -f ' + file + ' ' + command + ' ' + options

    logger.debug('Command to execute: ' + cmd)
    return subprocess.check_output(cmd, env={'DOCKER_HOST': ':2375'}, shell=True)

def openSwarmTunnel(config):
    url = getManagementEndpoint(config)
    cmd = 'ssh -L 2375:localhost:2375 -N ' + config.get('Cluster', 'username') + '@' + url + ' -p 2200'
    return "If you get errors ensure that you have craeted an SSH tunnel to your master by running '" + cmd + "'"

def openMesosTunnel(config):
    url = getManagementEndpoint(config)
    cmd = 'ssh -L 8080:localhost:8080 -N ' + config.get('Cluster', 'username') + '@' + url + ' -p 2200'
    return "If you get errors ensure that you have created an SSH tunnel to your master by running '" + cmd + "'"

def getAgentsFQDN(config):
    return config.get('Cluster', 'dnsPrefix') + 'agents.' + config.get('Cluster', 'region') + '.cloudapp.azure.com'

def getAgentHostNames(config):
    # WIP - do not use
    # return a list of Agent Host Names in this cluster
    cmd = "azure resource list -r Microsoft.Compute/virtualMachines " + config.get('Cluster', 'resourceGroup') +  " --json"
    os.system(cmd)

def installPackage(config):
    # WIP - do not use
    # Install a driver or other OS level package that is needed on the cluster
    logger = getLogger()
    url = getManagementEndpoint(config)
    package = "cifs-utils"
    sshConnection = "ssh " + config.get('Cluster', 'username') + '@' + url + ' -p 2200'
    logger.info("SSH Connection: " + sshConnection)
    sshCommand = "sudo apt-get install -qqq cifs-utils"
    command = sshConnection + " '" + sshCommand + "'"
    os.system(command)
