#!/usr/bin/python

import ConfigParser
import json
import logging
import os
import paramiko
import subprocess

output_dir = 'logs'
global logger 
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# create console handler and set level to info
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
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
    config.set('Group', 'name', config.get('ACS', 'dnsPrefix'))
    return config

def getACSParams(config):
    params = {}
    params["dnsNamePrefix"] = value(config.get('ACS', 'dnsPrefix'))
    params["agentCount"] = value(config.getint('ACS', 'agentCount'))
    params["agentVMSize"] = value(config.get('ACS', 'agentVMSize'))
    params["masterCount"] = value(config.getint('ACS', 'masterCount'))
    params["sshRSAPublicKey"] = value(config.get('ACS', 'sshPublicKey'))
    if config.get('ACS', 'orchestratorType') == 'mesos':
        params["adminPassword"] = value(config.get('ACS', 'password'))
    return params

def createResourceGroup(config):
    command = "azure group create " + config.get('Group', 'name')  + " " + config.get('Group', 'region')
    os.system(command)

def deleteResourceGroup(config):
    command = "azure group delete " + config.get('Group', 'name')
    os.system(command)

def createDeployment(config):
    logger = getLogger()
    logger.debug("Creating Deployment")
    logger.debug(json.dumps(getACSParams(config)))
    createResourceGroup(config)

    command = "azure group deployment create"
    command = command + " " + config.get('ACS', 'dnsPrefix')
    command = command + " " + config.get('ACS', 'dnsPrefix')
    command = command + " --template-uri " + config.get('Template', 'templateUrl')
    command = command + " -p '" + json.dumps(getACSParams(config)) + "'"
    
    os.system(command)

def createStorage(config):
    logger = getLogger()
    logger.debug("Creating Storage Account")
    createResourceGroup(config)
    
    command = "azure storage account create"
    command = command + " --type " + config.get('Storage', 'type')
    command = command + " --resource-group " + config.get('Group', 'name')
    command = command + " --location " + config.get('Group', 'region')
    command = command + " " + config.get('Storage', 'name')
    
    os.system(command)

    key = getStorageAccountKey(config)

    try:
        command = "azure storage share create"
        command = command + " --account-name " + config.get('Storage', 'name')
        command = command + " --account-key " + key
        command = command + " " + config.get('Storage', 'shareName')

        out = subprocess.check_output(command, shell=True)
    except:
        # FIXME: test if the share already exists, if it does then don't try to recreate it
        # For now we just assume that an error is always that the share alrady exists 
        logger.warning("Failed to create share, assuming it is because it already exists")

def getStorageAccountKey(config):
    command = "azure storage account keys list"
    command = command + " --resource-group " + config.get('Group', 'name')
    command = command + " " + config.get('Storage', 'name')
    command = command + " --json"

    keys = json.loads(subprocess.check_output(command, shell=True))
    return keys['storageAccountKeys']['key1']


def getShareEndpoint(config):
    command = "azure storage account show"
    command = command + " --resource-group " + config.get('Group', 'name')
    command = command + " " + config.get('Storage', 'name')
    command = command + " --json"

    data = json.loads(subprocess.check_output(command, shell=True))
    endpoint = data['primaryEndpoints']['file']

    return endpoint

def getManagementEndpoint(config):
    return config.get('ACS', 'dnsPrefix') + 'mgmt.' + config.get('Group', 'region').replace(" ", "").replace('"', '') + '.cloudapp.azure.com'

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
    cmd = 'ssh -L 2375:localhost:2375 -N ' + config.get('ACS', 'username') + '@' + url + ' -p 2200'
    return "If you get errors ensure that you have craeted an SSH tunnel to your master by running '" + cmd + "'"

def openMesosTunnel(config):
    url = getManagementEndpoint(config)
    cmd = 'ssh -L 8080:localhost:8080 -N ' + config.get('ACS', 'username') + '@' + url + ' -p 2200'
    return "If you get errors ensure that you have created an SSH tunnel to your master by running '" + cmd + "'"

def getAgentsFQDN(config):
    return config.get('ACS', 'dnsPrefix') + 'agents.' + config.get('Group', 'region') + '.cloudapp.azure.com'

def getAgentHostNames(config):
    # return a list of Agent Host Names in this cluster
    
    cmd = "azure resource list -r Microsoft.Compute/virtualMachines " + config.get('Group', 'name') +  " --json"
    logger.debug("Execute command: " + cmd)

    agents = json.loads(subprocess.check_output(cmd, shell=True))
    names = []
    for agent in agents:
        name = agent['name']
        if "-agent-" in name:
            names.append(name)
    return names

def getMasterSSHConnection(config):
    url = getManagementEndpoint(config)
    return "ssh " + config.get('ACS', 'username') + '@' + url + ' -p 2200'

def configureSSH(config):
    # Configure SSH on the master
    logger = getLogger()
    url = getManagementEndpoint(config)
    conn = "scp -P 2200"
    localfile = "~/.ssh/id_rsa"
    remotefile = config.get('ACS', 'username') + '@' + url + ":~/.ssh/id_rsa"
    
    cmd = conn + " " + localfile + " " + remotefile
    logger.debug("SCP command: " + cmd)

    out = subprocess.check_output(cmd, shell=True)

def addAzureFileService(config, hosts):
    # Add an Azure File Service to identified agents
    logger = getLogger()
    url = getManagementEndpoint(config)
    package = "cifs-utils"

    sshMasterConnection = getMasterSSHConnection(config)
    logger.debug("SSH Master Connection: " + sshMasterConnection)

    for host in hosts:
        sshAgentConnection = "ssh -o StrictHostKeyChecking=no " + config.get('ACS', 'username') + '@' + host
        logger.debug("SSH Agent Connection: " + sshAgentConnection)

        mount = config.get("Storage", "mount")
        sshCommand = "mkdir -p " + mount
        logger.debug("Command to run: " + sshCommand)
    
        cmd = sshMasterConnection + ' "' + sshAgentConnection + ' \'' + sshCommand + '\'"'
        out = subprocess.check_output(cmd, shell=True)
        logger.debug("Output:\n" + out)

        urn = getShareEndpoint(config).replace("https:", "") + config.get("Storage", "shareName")
        username = config.get("Storage", "name")
        password = getStorageAccountKey(config)
        sshCommand = "sudo mount -t cifs " + urn + " " + mount + " -o uid=1000,gid=1000,vers=2.1,username=" + username + ",password=" + password
        logger.debug("Command to run: " + sshCommand)
        cmd = sshMasterConnection + ' "' + sshAgentConnection + ' \'' + sshCommand + '\'"'
        out = subprocess.check_output(cmd, shell=True)
        logger.debug("Output:\n" + out)
