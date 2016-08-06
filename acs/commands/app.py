""" 

Deploy and manage applications to Azure Container Service.

Usage:
  app <command> [help] [options]

Commands:
  deploy                deploy an application described by the appropriate app configuration

Options:
  --app-config=<file>   the application configuration (compose file for Docker Swarm, Marhon JSON for DC/OS).
                        Note that some special values in this file will be replaced, for example, $AGENT_FQDN
                        will be replaced with the Fully Qualifed Domain Name of the public agent pool.

Help:
  For help using the oms command please open an issue at 
  https://github.com/rgardler/acs-scripts
"""

from docopt import docopt
from inspect import getmembers, ismethod
from json import dumps
import os
import subprocess as sub 

from .base import Base

class App(Base):

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

  def deploy(self):
    app_config_dir = "~/.acs/app/"

    config_path = self.args["--app-config"]
    if not config_path:
      self.log.error("--app-config not supplied, unable to deploy application")
      return "Must provide an application config file as '--app-config'"
    
    self.log.debug("Deploying application described by " + config_path)
    config_filename = os.path.expanduser(config_path)
    perm_filename = os.path.expanduser(app_config_dir + config_filename)
    os.makedirs(os.path.dirname(perm_filename), exist_ok=True)

    tmpl = open(config_filename)
    output = open(perm_filename, 'w')
    for s in tmpl:
        s = s.replace("$AGENT_FQDN", self.getAgentEndpoint())
        output.write(s)

    tmpl.close()
    output.close()

    p = sub.Popen(['dcos', 'marathon', 'app', "add", perm_filename],stdout=sub.PIPE,stderr=sub.PIPE)
    output, errors = p.communicate()
    if errors:
      self.log.error("Error deploying applicatoin:\n" + errors.decode("utf-8"))
      return "Unable to deploy application, see log for full details."
    self.log.debug("Application deployed. Configuration stored in " + perm_filename)

    return "Application deployed"
