"""Configure demo's for the user. Wherever possible the process is to be
fully automated but in some cases there are manual steps
involved. These are documented in the commadn output.

Usage:
  demo <command> [help] [options]

Commands:
  lbweb        Deploy a load balanced web application

Options:
  --remove     Remove the demo rather than deploy it

Help:
  For help using the oms command please open an issue at 
  https://github.com/rgardler/acs-scripts

"""

import acs.cli
from .base import Base
from .service import Service
from .dcos import Dcos
from .app import App

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


  def lbweb(self):
    """
    Deploy or remove a simple load balanced web application.
    """
    args = self.args
    self.log.debug("`demo lbweb` args before adding app-config:\n" + str(args))
    args["--app-config"] = "config/demo/web/simple-web.json"

    app = App(self.config, self.options)
    app.args = args

    if self.args["--remove"]:
      return app.remove()
    
    print(acs.cli.login())

    service = Service(self.config, self.options)
    service.create()
    service.openTunnel()

    cmd = ["dcos package install marathon-lb --yes"]
    output, errors = self.shell_execute(cmd)
    self.log.debug(output)
    if "successfully installed!" not in output:
      if "already installed" not in errors:
        self.log.error("Output of dcos package install does not include 'successfuly installed!' and it is not already installed");
        raise OSError("Failed to install Marathon-lb")

    return app.deploy()


    
