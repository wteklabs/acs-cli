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
  --tag=<DOCKER_TAG>    If specified in the app-config file this tag will be used to customize the Docker tag used.


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

  def parseAppConfig(self, config_path, tokens = {}):
    """
    Parse a use provided application configuration, replacing any
    tokens that appear within it as appropriate. The parsed file
    will be stored in `~/.acs/app/config/`.

    Available tokens are:

    ${AGENT_FQDN}  - replaced with the FQDN of the agent cluster
    ${DOCKER_TAG} - replaced with the value of the command line parameter `--tag` (default `latest`)
    ${FOO_BAR} - replaced with the value of 'FOO_BAR' in the supplied dictionary of tokens

    """
    if not config_path:
      self.logger.error("--app-config not supplied, unable to deploy application")
      raise IOError("Must provide an application config file as '--app-config'")

    if "--tag" in self.args:
      if self.args["--tag"] == "":
        tag = "latest"
      else:
        tag = self.args["--tag"]
    else:
      tag = "latest"

      
    self.logger.debug("Deploying application described by " + config_path)
    self.logger.debug("Using Docker tag of " + tag)

    config_filename = os.path.expanduser(config_path)
    perm_filename = os.path.expanduser(self.app_config_dir + config_filename)
    os.makedirs(os.path.dirname(perm_filename), exist_ok=True)

    tmpl = open(config_filename)
    output = open(perm_filename, 'w')
    for s in tmpl:
        s = s.replace("${AGENT_FQDN}", self.getAgentEndpoint())
        s = s.replace("${DOCKER_TAG}", tag)
        if "${" in s:
          start = s.index("${")
          end = s.index("}", start)
          name = s[start + 2:end]
          self.logger.debug("Replacing token " + name)
          if name in tokens:
            value = tokens[name]
            self.logger.debug("with " + value)
            s= s.replace("${" + name + "}", value)
          else:
            self.logger.debug("no value for token provided")
        output.write(s)

    tmpl.close()
    output.close()

    return perm_filename
    
  def deploy(self, tokens = None):
    """Deploy the application (or group of applications defined in the
    file referenced in `--app-config`. The command will block until
    the deployment either succeeds.

    If the application is already deployed a `RuntimeWarning` will be
    raised.

    Other errors will trigger a 'RuntimeWarning'.

    tokens is a dictionary continaing key value pairs that will be
    used as substitutes in the application configuration file. That
    is, if the cofig file contains ${FOO_BAR} then it will be replaced
    with the value of "FOO_BAR" in the tokens dictionary.

    """
    config_path = self.args["--app-config"]
    try:
      perm_filename = self.parseAppConfig(config_path, tokens)
    except IOError as e:
      self.logger.error("Problem finding the application configuration.\n" + str(e))
      raise e

    dcos = Dcos(self.acs)
    with open(perm_filename) as config_file:
      app_config = json.load(config_file)

    appId = app_config["id"]
    self.logger.debug("App/Group to be deployed has id: " + appId)
      
    if "apps" in app_config:
      cmd = "marathon group add " + perm_filename
    else:
      cmd = "marathon app add " + perm_filename
    output, errors = dcos.execute(cmd)

    if errors:
      msg = "Error deploying application:\n" + errors
      self.logger.error(msg)
      raise RuntimeWarning(msg)

    isDeployed = False
    while not isDeployed:
      cmd = "marathon deployment list " + appId + " --json"
      output, errors = dcos.execute(cmd)
      if errors:
        msg = "Unable to get deployment list:\n" + errors
        self.logger.error(msg)
        raise RuntimeWarning(msg)
      time.sleep(0.5)

      deployments = json.loads(output)
      if len(deployments) == 0:
        isDeployed = True
    
    self.logger.debug("Application deployed. Configuration stored in " + perm_filename)

    return "Application deployed"

  def remove(self, tokens = None):
    config_path = self.args["--app-config"]

    dcos = Dcos(self.acs)
    try:
      perm_filename = self.parseAppConfig(config_path)
      with open(perm_filename) as config_file:
        app_config = json.load(config_file)
    except IOError as e:
      self.logger.error(e)
      raise e

    app_id = app_config["id"]
    self.logger.debug("Removing app with the ID " + app_id)
    
    if "apps" in app_config:
      cmd = "marathon group remove " + app_id + " --force"
    else:
      cmd = "marathon app remove " + app_id + " --force"
    output, errors = dcos.execute(cmd)

    if errors:
      self.logger.error("Error removing application:\n" + errors)
      return "Unable to remove application, see log for full details."
    self.logger.debug("Application removed. Configuration stored in " + perm_filename)

    return "Application removed."
