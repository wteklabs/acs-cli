"""The base command class. All implemented commands should extend this class."""
from ..AgentPool import AgentPool

import json
import paramiko
from paramiko import SSHClient

class Base(object):

  def __init__(self, config, options, *args, **kwargs):
    self.log = ACSLog("Base")
    self.config = config
    self.options = options
    self.args = args
    self.kwargs = kwargs

    self.ssh = SSHClient()
    self.ssh.load_system_host_keys()
    self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    self.ssh.connect(self.getManagementEndpoint(), username = self.config.get('ACS', "username"), port=2200)

  def run(self):
    raise NotImplementedError("You must implement the run() method in your commands")

  def help(self):
    raise NotImplementedError("You must implement the help method. In most cases you will simply do 'print(__doc__)'")

  def getManagementEndpoint(self):
    return self.config.get('ACS', 'dnsPrefix') + 'mgmt.' + self.config.get('Group', 'region').replace(" ", "").replace('"', '') + '.cloudapp.azure.com'

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

  def executeOnAgent(self, cmd, agent_name):
    """
    Execute command on an agent identified by agent_name
    """
    sshAgentConnection = "ssh -o StrictHostKeyChecking=no " + self.config.get('ACS', 'username') + '@' + agent_name
    self.log.debug("SSH Connection to agent: " + sshAgentConnection)
    
    self.log.debug("Command to run on agent: " + cmd)
    
    cmd = cmd.replace("\"", "\\\"")
    sshCmd = sshAgentConnection + ' \'' + cmd + '\''
    self.executeOnMaster(sshCmd)

  def executeOnMaster(self, cmd):
    """
    Execute command on the current master leader
    """
    self.log.debug("Executing on master: " + cmd)
    stdin, sterr, stdout = self.ssh.exec_command(cmd)
    stdin.close()

    for line in stdout.read().splitlines():
      self.log.debug(line)

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
    params["sshRSAPublicKey"] = self.value(self.get('ACS', 'sshPublicKey'))
    return params

