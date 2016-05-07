"""

Create an manage instances of Azure Container Service. The service
configuration is defined in the `cluster.ini` file (or the file
specified in `--config-file`.

Usage:
  service <command> [help] [options]

Commands:
  create                create an Azure Container Service
  delete                delete an Azure Container Service
  show                  display the current service configuration

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
        if result is None:
          result = command + " returned no results"
    if result:
      print(result)
    else:
      print("Unknown command: '" + command + "'")
      self.help()
   	  
  def help(self):
    print(__doc__)

  def create(self):
    self.log.debug("Creating ACS Deployment")
    self.log.debug(json.dumps(self.config.getACSParams()))

    Base.createResourceGroup(self)
    
    command = "azure group deployment create"
    command = command + " " + self.config.get('ACS', 'dnsPrefix')
    command = command + " " + self.config.get('ACS', 'dnsPrefix')
    command = command + " --template-uri " + self.config.get('Template', 'templateUrl')
    command = command + " -p '" + json.dumps(self.config.getACSParams()) + "'"
    
    os.system(command)

  def delete(self):
    self.log.debug("Deleting ACS Deployment")
    self.log.debug(json.dumps(self.config.getACSParams()))
    
    command = "azure container delete"
    command = command + " " + self.config.get('ACS', 'dnsPrefix')
    command = command + " containerservice-" + self.config.get('ACS', 'dnsPrefix')
    os.system(command)
    
    # FIXME: we shouldn't need to do the group delete, but currently container delete is not a deep delete
    print("'azure container delete 'does not currently delete resources created within the container service. You can delete all resources by also deleting the associated resource group, however, be aware this will delete everything in the resource group.")
    command = "azure group delete " + self.config.get('Group', 'name')
    os.system(command)

  def show(self):
    """
    Output the configuration of this cluster in json format.
    """
    config = self.getClusterSetup()
    return json.dumps(config, sort_keys=True,
                      indent=4, separators=(',', ': '))

