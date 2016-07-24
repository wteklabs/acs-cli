""" 

Provides a pass trough to the DCOS command line, along with 
a convenience to install the DCOS CLI.

Usage:
  install <command> [help] [options]

Commands:
  install               install the DCOS CLI. Must have run `acs service openTunnel` first.

Help:
  For help using the oms command please open an issue at 
  https://github.com/rgardler/acs-scripts
"""

from docopt import docopt
from inspect import getmembers, ismethod
from json import dumps
import os

from .base import Base

class Dcos(Base):

  def run(self):
    args = docopt(__doc__, argv=self.options)
    # print("Command args")
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

  def install(self):
    if self.config.get('ACS', 'orchestratorType') != 'DCOS':
      return false

    self.log.info("Installing DCOS CLI")

    cmd = "pip install virtualenv"
    os.system(cmd)

    cmd = "mkdir dcos && cd dcos"
    os.system(cmd)

    cmd = "wget https://raw.githubusercontent.com/mesosphere/dcos-cli/master/bin/install/install-optout-dcos-cli.sh"
    os.system(cmd)

    cmd = "chmod +x install-optout-dcos-cli.sh"
    os.system(cmd)

    cmd = "./install-optout-dcos-cli.sh . http://localhost --add-path yes"
    os.system(cmd)

    return "DCOS installed, but to configure it properly you need to run `source /src/bin/env-setup`"
