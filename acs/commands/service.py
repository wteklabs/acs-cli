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

from docopt import docopt
from inspect import getmembers, ismethod
from json import dumps

from .base import Base

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
    raise Exception("FIXME: Implement the ACS create commad")
