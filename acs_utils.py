#!/usr/bin/python

import ConfigParser
import json
import os


def value(set_to):
    value = {}
    value["value"] = set_to
    return value

def getConfig():
    config = ConfigParser.ConfigParser()
    config.read("cluster.ini")
    return config

def getClusterParams(config):
    params = {}
    params["adminUsername"] = value(config.get('Cluster', 'username'))
    params["adminPassword"] = value(config.get('Cluster', 'password'))
    params["DNSNamePrefix"] = value(config.get('Cluster', 'dns_prefix'))
    params["agentCount"] = value(config.getint('Cluster', 'agent_count'))
    params["masterCount"] = value(config.getint('Cluster', 'master_count'))
    params["sshRSAPublicKey"] = value(config.get('Cluster', 'ssh_public_key'))
    return params

def createResourceGroup(config):
    command = "azure group create " + config.get('Cluster', 'dns_prefix') + " " + config.get('Cluster', 'region')
    os.system(command)

def deleteResourceGroup(config):
    command = "azure group delete " + config.get('Cluster', 'dns_prefix')
    os.system(command)

def createDeployment(config):
    createResourceGroup(config)

    command = "azure group deployment create"
    command = command + " " + config.get('Cluster', 'dns_prefix')
    command = command + " " + config.get('Cluster', 'dns_prefix')
    command = command + " --template-uri " + config.get('Template', 'template_url')
    command = command + " -p '" + json.dumps(getClusterParams(config)) + "'"
    
    os.system(command)

def getManagementEndpoint(config):
    return config.get('Cluster', 'dns_prefix') + 'man.' + config.get('Cluster', 'region') + '.cloudapp.azure.com'

def marathonCommand(config, command, method = 'GET'):
    url = getManagementEndpoint(config)
    curl = 'curl -s -X ' + method + ' localhost:8080/v2/' + command
    cmd = 'ssh ' + config.get('Cluster', 'username') + '@' + url + ' -p 2211 ' + curl
    os.system(cmd)
