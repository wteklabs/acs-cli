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
  openTunnel            open an SSH tunnel to the management interface

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
import subprocess
import sys  

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

  def exists(self):
    """ Tests whether the management endpoint is accessible, if it is we assume the service exists """
    exists = Base._hostnameResolves(self, Base.getManagementEndpoint(self))
    if exists:
      return True
    else:
      return False

  def create(self):
    if self.exists():
      return "It appears that the cluster already exists:\n" + self.show()

    self.log.debug("Creating ACS Deployment")
    self.log.debug(json.dumps(self.config.getACSParams()))

    Base.createResourceGroup(self)
    
    command = "azure group deployment create"
    command = command + " " + self.config.get('ACS', 'dnsPrefix')
    command = command + " " + self.config.get('ACS', 'dnsPrefix')
    command = command + " --template-uri " + self.config.get('Template', 'templateUrl')
    command = command + " -p '" + json.dumps(self.config.getACSParams()) + "'"
    
    os.system(command)

    if self.exists():
      return self.show()

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

  def openTunnel(self):
    """
    Open an SSH tunnel to the management endpoint.
    """
    try:
      pid = os.fork()
      if pid > 0:
        # Exit parent process
        sys.exit(0)
    except OSError, e:
        print >> sys.stderr, "fork failed: %d (%s)" % (e.errno, e.strerror)
        sys.exit(1)

    # Configure the child processes environment
    os.chdir("/")
    os.setsid()
    os.umask(0)

    pid = os.getpid()
    print("To stop the SSH tunnel run 'kill " + str(os.getpid()) + "'")

    Base.openTunnel(self)
    return pid

  def marathonCommand(self, command, method = 'GET', data = None):
    curl = 'curl -s -X ' + method 
    if data != None:
      curl = curl + " -d \"" + data + "\" -H \"Content-type:application/json\""
    cmd = curl + ' localhost/marathon/v2/' + command 
    self.log.debug('Command to execute: ' + cmd)
    return Base.sshTunnel(self, cmd)

