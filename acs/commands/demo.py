"""Configure demo's for the user. Wherever possible the process is to be
fully automated but in some cases there are manual steps
involved. These are documented in the commadn output.

Usage:
  demo <command> [help] [options]

Commands:
  microscaling_services    Demonstrate microscaling of services

Options:

Help:
  For help using the oms command please open an issue at 
  https://github.com/rgardler/acs-scripts

"""

from .base import Base
from .service import Service

from docopt import docopt
from inspect import getmembers, ismethod
from json import dumps


class Demo(Base):

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

  def microscaling_services(self):
      # deploy the 4 containers
      self.deploy_marathon_app("/config/remainder.json")
      self.deploy_marathon_app("/config/producer.json")
      self.deploy_marathon_app("/config/consumer.json")
      self.deploy_marathon_app("/config/microscaling.json")
      # provide login details
      # display the script

  def deploy_marathon_app(self, filename):
      service = Service(self.config, {})
      with open(filename, 'r') as data_file:
          app = data_file.read().replace("\"", "\\\"")
      service.marathonCommand('apps', 'POST', app)
