""" 

Deploy and manage applications to Azure Container Service.

Usage:
  app <command> [help] [options]

Commands:
  deploy                deploy an application described by the appropriate app configuration
  remove                remove an application described by the appropriate app configuration from the cluster

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
import json
from json import dumps
import os
import subprocess as sub 

from .base import Base

class App(Base):
  app_config_dir = "~/.acs/app/"

  def run(self):
    args = docopt(__doc__, argv=self.options)
    # self.log.debug("App options:" + str(self.options))
    # self.log.debug("App args:" + str(args))
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

  def parseAppConfig(self, config_path):
    """
    Parse a use provided application configuration, replacing any
    tokens that appear within it as appropriate. The parsed file
    will be stored in `~/.acs/app/config/`.
    """
    if not config_path:
      self.log.error("--app-config not supplied, unable to deploy application")
      raise IOError("Must provide an application config file as '--app-config'")

    self.log.debug("Deploying application described by " + config_path)
    config_filename = os.path.expanduser(config_path)
    perm_filename = os.path.expanduser(self.app_config_dir + config_filename)
    os.makedirs(os.path.dirname(perm_filename), exist_ok=True)

    tmpl = open(config_filename)
    output = open(perm_filename, 'w')
    for s in tmpl:
        s = s.replace("$AGENT_FQDN", self.getAgentEndpoint())
        output.write(s)

    tmpl.close()
    output.close()

    return perm_filename
    
  def deploy(self):
    config_path = self.args["--app-config"]
    try:
      perm_filename = self.parseAppConfig(config_path)
    except IOError as e:
      self.log.error(str(e))
      return "Unable to deploy application. There is a problem with the app configuration file. See the log for full details."

    p = sub.Popen(['dcos', 'marathon', 'app', "add", perm_filename],stdout=sub.PIPE,stderr=sub.PIPE)
    output, errors = p.communicate()
    if errors:
      self.log.error("Error deploying application:\n" + errors.decode("utf-8"))
      return "Unable to deploy application, see log for full details."
    self.log.debug("Application deployed. Configuration stored in " + perm_filename)

    return "Application deployed"

  def remove(self):
    config_path = self.args["--app-config"]
    try:
      perm_filename = self.parseAppConfig(config_path)
      with open(perm_filename) as app_config: 
        app = json.load(app_config)
        app_id = app["id"]
    except IOError as e:
      self.log.error(e)
      return "Unable to remove application because: " + str(e) + ". See the log for full details."

    self.log.debug("Removing app with the ID " + app_id)
    p = sub.Popen(['dcos', 'marathon', 'app', "remove", app_id],stdout=sub.PIPE,stderr=sub.PIPE)
    output, errors = p.communicate()
    if errors:
      self.log.error("Error removing application:\n" + errors.decode("utf-8"))
      return "Unable to remove application, see log for full details."
    self.log.debug("Application removed. Configuration stored in " + perm_filename)

    return "Application removed."
