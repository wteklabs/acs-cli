"""

Create and manage instances of Azure Container Service. The service
configuration is defined in the `cluster.ini` file (or the file
specified in `--config-file`.

Usage:
  service <command> [help] [options]
  service execOnMaster <command>

Commands:
  create                create an Azure Container Service
  delete                delete an Azure Container Service
  scale                 Scale the agent cluster up
  show                  display the current service configuration
  connect               open an SSH tunnel to the management interface
  disconnect            close the current SSH tunnel
  execOnMaster          execute a command on the lead master
  shutdown              shutdown all the vms in your cluster

Options:
  --agents=<number>            number of agents (currently scale only scale up is supported)
  --quiet                      don't ask the user for input
Examples:

Make the number of agents in the primary pool 5
  acs service scale --agents=5

Help:
  For help using the oms command please open an issue at 
  https://github.com/rgardler/acs-scripts

"""
from .base import Base
from ..acs import Acs
from ..dcos import Dcos

from docopt import docopt
from inspect import getmembers, ismethod
import json
import os
import subprocess
import sys  
from tempfile import mkstemp
import signal
import time
from time import sleep
import urllib.request
from shutil import move
from os import remove, close

class Service(Base):

  def run(self):
    args = docopt(__doc__, argv=self.options)
    # self.logger.debug("Service args")
    # self.logger.debug(args)
    self.args = args
    
    command = self.args["<command>"]
    result = None

    self.acs = Acs(self.config)
    
    if self.args["execOnMaster"]:
      print(self.execOnMaster(command))
      return

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
    return self.acs.exists()

  def create(self):
    """ Deploy an instance of ACS """
    return self.acs.create()
  
  def install_dcos_cli(self):
    """DEPRECATED as of 1.12: use Dcos.installCli() instead.

    """
    dcos = Dcos(self.acs)
    return dcos.install_cli()
    
  def delete(self, quiet = False):
    """ Delete an instance of ACS. """
    return self.acs.delete(quiet)

  def show(self):
    """
    Output the configuration of this cluster in json format.
    """
    config = self.getClusterSetup()
    return json.dumps(config, sort_keys=True,
                      indent=4, separators=(',', ': '))

  def openTunnel(self):
    """DEPRECATED: use connect() instead"""
    self.connect()
    self.logger.warning("Service.openTunnel() is deprecated. Please use Service.connect instead.")
  
  def connect(self):
    """Open an SSH tunnel to the management endpoint, if one doesn't
    already exist. The PID for the tunnel is written to
    `~/.acs/ssh.pid`.  If a tunnel already exiss then a new one will
    not be created instead PID for the existing tunnel will be
    returned.

    This method attempts to block until we have an active connection
    to the master endpoint.

    """
    return self.acs.connect()
    
  def closeTunnel(self):
    """DEPRECATED: use disconnect() instead"""
    self.disconnect()
    self.logger.warningxo("Service.closeTunnel() is deprecated. Please use Service.disconnect instead.")
  
  def disconnect(self):
    """
    Close the SSH tunnel to the management endpoint with the supplied pid
    """
    return self.acs.disconnect()

  def scale(self):
    desired_agents = self.args["--agents"]
    self.acs.scale(desired_agents)
    
  def execOnMaster(self, command):
    """
    Execute the supplied sommand on the lead master.
    """
    return self.acs.executeOnMaster(command)
        
  def shutdown(self):
    return self.acs.shutdown()
