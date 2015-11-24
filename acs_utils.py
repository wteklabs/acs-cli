#!/usr/bin/python

import ConfigParser
import json
import logging
import os

logger = logging.getLogger()

def initializeLog(output_dir):
    global logger
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

def value(set_to):
    value = {}
    value["value"] = set_to
    return value

def getConfig(filename = "cluster.ini"):
    initializeLog('logs')
    defaults = {"orchestratorType": "Mesos", "jumpboxOS": "Linux"}
    config = ConfigParser.ConfigParser(defaults)
    config.read(filename)
    return config

def getClusterParams(config):
    params = {}
    params["serviceName"] = value(config.get('Cluster', 'dnsPrefix'))
    params["orchestratorType"] = value(config.get('Cluster', 'orchestratorType'))
    params["adminUsername"] = value(config.get('Cluster', 'username'))
    params["adminPassword"] = value(config.get('Cluster', 'password'))
    params["DNSNamePrefix"] = value(config.get('Cluster', 'dnsPrefix'))
    params["agentCount"] = value(config.getint('Cluster', 'agentCount'))
    params["masterCount"] = value(config.getint('Cluster', 'masterCount'))
    params["sshRSAPublicKey"] = value(config.get('Cluster', 'sshPublicKey'))
    return params

def createResourceGroup(config):
    command = "azure group create " + config.get('Cluster', 'dnsPrefix') + " " + config.get('Cluster', 'region')
    os.system(command)

def deleteResourceGroup(config):
    command = "azure group delete " + config.get('Cluster', 'dns_prefix')
    os.system(command)

def createDeployment(config):
    global logger
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
    return config.get('Cluster', 'dns_prefix') + 'man.' + config.get('Cluster', 'region') + '.cloudapp.azure.com'

def marathonCommand(config, command, method = 'GET'):
    url = getManagementEndpoint(config)
    curl = 'curl -s -X ' + method + ' localhost:8080/v2/' + command
    cmd = 'ssh ' + config.get('Cluster', 'username') + '@' + url + ' -p 2211 ' + curl
    os.system(cmd)

    