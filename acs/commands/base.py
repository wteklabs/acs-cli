"""The base command class. All implemented commands should extend this class."""
import json

class Base(object):

  def __init__(self, config, options, *args, **kwargs):
    self.log = ACSLog("Base")
    self.config = config
    self.options = options
    self.args = args
    self.kwargs = kwargs

  def run(self):
    raise NotImplementedError("You must implement the run() method in your commands")

  def help(self):
    raise NotImplementedError("You must implement the help method. In most cases you will simply do 'print(__doc__)'")


"""The cofiguration for an ACS cluster to work with"""
from acs.ACSLogs import ACSLog

import ConfigParser
import os 

class Config(object):
  def __init__(self, filename):
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

