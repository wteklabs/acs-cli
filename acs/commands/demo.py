"""Configure demo's for the user. Wherever possible the process is to be
fully automated but in some cases there are manual steps
involved. These are documented in the commadn output.

Usage:
  demo <command> [help] [options]

Commands:
  lbweb        Deploy a load balanced web application

Options:

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
    print(acs.cli.login())

    service = Service(self.config, self.options)
    service.create()
    service.openTunnel()

    dcos = Dcos(self.config, self.options)
    dcos.install()
    cmd = [".", "/src/bin.env-setup"]
    result = self.shell_execute(cmd)
    self.log.debug(result)
    
    cmd = ["dcos", "package", "install", "marathon-lb", "--yes"]
    result = self.shell_execute(cmd)
    self.log.debug(result)

    args = self.args
    args["--app-config"] = "config/demo/web/simple-web.json"
    app = App(self.config, self.options)
    app.args = args
    return app.deploy()
