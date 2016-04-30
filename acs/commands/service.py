"""

Create an manage instances of Azure Container Service. The service
configuration is defined in the `cluster.ini` file (or the file
specified in `--config-file`.

Usage:
  service <command> [help] [options]

Commands:
  create                create the azure container service

Options:

Help:
  For help using the oms command please open an issue at 
  https://github.com/rgardler/acs-scripts

"""
from .base import Base

from docopt import docopt
from inspect import getmembers, ismethod
import json
import os

class Service(Base):

  def run(self):
    args = docopt(__doc__, argv=self.options)
    # print("Global args")
    # print(args)
    self.args = args
    
    command = self.args["<command>"]
    result = None
    methods = getmembers(self, predicate = ismethod)
    for name, method in methods:
      if name == command:
        result = method()
    if result:
      print(result)
    else:
      print("Unknown command: '" + command + "'")
      self.help()
   	  
  def help(self):
    print(__doc__)

  def create(self):
    self._createDeployment()
    raise Exception("FIXME: Implement the ACS create commad")

  def _createResourceGroup(self):
    command = "azure group create " + self.config.get('Group', 'name')  + " " + self.config.get('Group', 'region')
    os.system(command)

  def _deleteResourceGroup(self):
    command = "azure group delete " + self.config.get('Group', 'name')
    self.log.info("Command: " + command)
    os.system(command)

  def _createDeployment(self):
    self.log.debug("Creating Deployment")
    self.log.debug(json.dumps(self.config.getACSParams()))
    self._createResourceGroup()
    
    command = "azure group deployment create"
    command = command + " " + self.config.get('ACS', 'dnsPrefix')
    command = command + " " + self.config.get('ACS', 'dnsPrefix')
    command = command + " --template-uri " + self.config.get('Template', 'templateUrl')
    command = command + " -p '" + json.dumps(self.config.getACSParams()) + "'"
    
    os.system(command)

