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

from .base import Base
from ..dcos import Dcos

from docopt import docopt
from inspect import getmembers, ismethod
import json
from json import dumps
import os
import time

class App(Base):
  app_config_dir = "~/.acs/app/"

  def run(self):
    args = docopt(__doc__, argv=self.options)
    # self.logger.debug("App options:" + str(self.options))
    # self.logger.debug("App args:" + str(args))
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
      self.logger.error("--app-config not supplied, unable to deploy application")
      raise IOError("Must provide an application config file as '--app-config'")

    self.logger.debug("Deploying application described by " + config_path)
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
    """Deploy the application dfined in the file referenced in
    `--app-config`. The command will block until the deployment
    either succeeds.

    If the application is already deployed a `RuntimeWarning` will be
    raised.

    Other errors will trigger a 'RuntimeWarning'.

    """
    config_path = self.args["--app-config"]
    try:
      perm_filename = self.parseAppConfig(config_path)
    except IOError as e:
      self.logger.error("Unable to deploy applicatoin.\n" + str(e))
      raise e

    dcos = Dcos(self.acs)
    cmd = "marathon app add " + perm_filename
    output, errors = dcos.execute(cmd)
    if errors:
      msg = "Error deploying application:\n" + errors
      self.logger.error(msg)
      raise RuntimeWarning(msg)

    # FIXME: get appId from the app config
    appId ="/web"

    isDeployed = False
    while not isDeployed:
      cmd = "marathon deployment list " + appId + " --json"
      output, errors = dcos.execute(cmd)
      if errors:
        msg = "Unable to get deployment list:\n" + errors
        self.logger.exception(e)
        raise RuntimeWarning(msg)
      time.sleep(0.5)
      
      if not output is None:
        if "There are no deployments" in output:
          isDeployed = True
    
    self.logger.debug("Application deployed. Configuration stored in " + perm_filename)

    return "Application deployed"

  def remove(self):
    config_path = self.args["--app-config"]
    try:
      perm_filename = self.parseAppConfig(config_path)
      with open(perm_filename) as app_config: 
        app = json.load(app_config)
        app_id = app["id"]
    except IOError as e:
      self.logger.error(e)
      raise e

    self.logger.debug("Removing app with the ID " + app_id)
    dcos = Dcos(self.acs)
    cmd = "marathon app remove " + app_id
    output, errors = dcos.execute(cmd)
    if errors:
      self.logger.error("Error removing application:\n" + errors)
      return "Unable to remove application, see log for full details."
    self.logger.debug("Application removed. Configuration stored in " + perm_filename)

    return "Application removed."
