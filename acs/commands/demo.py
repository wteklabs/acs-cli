"""Configure demo's for the user. Wherever possible the process is to be
fully automated but in some cases there are manual steps
involved. 

Usage:
  demo <command> [help] [options]

Commands:
  lbweb         Deploy a load balanced web application
  management    Deploy a master proxy that will allow (insecure) access to the DC/OS UI through http://AGENTS_FQDN:8080
  microscaling  Deploy an example of a multi-container application with microscaling support.
  smack         Deploy the Smack stack

Options:
  --remove          Remove the demo rather than deploy it
  --tag=<VERSION>   The version tag for the application

Help:
  For help using the oms command please open an issue at 
  https://github.com/rgardler/acs-scripts

"""

import acs.cli
from .base import Base
from .lb import Lb
from .service import Service
from .app import App
from ..dcos import Dcos
from ..storage import Storage

from docopt import docopt
from inspect import getmembers, ismethod
import json
import time

class Demo(Base):

  def run(self):
    args = docopt(__doc__, argv=self.options)
    # self.logger.debug("Command args")
    # self.logger.debug(args)
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
    self.logger.debug("`demo lbweb` args before adding app-config:\n" + str(args))
    args["--app-config"] = "/src/config/demo/web/simple-web.json"

    app = App(self.config, self.options)
    app.args = args

    if self.args["--remove"]:
      return app.remove()
    
    print(acs.cli.login())

    service = Service(self.config, self.options)
    service.create()
    service.connect()

    service.install_dcos_cli()
    
  def dcos_package_install(self, package):
    dcos = Dcos(self.acs)
    cmd = "package install " + package + " --yes"
    result = dcos.execute(cmd)
    if result is not None:
      output = result[0]
      errors = result[1]
      
    if "successfully installed!" not in output and "being installed" not in output:
      if "already installed" not in errors:
        self.logger.error("Output of dcos package install does not include 'successfuly installed!' and it is not already installed");
        raise OSError("Failed to install " + package)

    return output, errors

  def smack (self):
    """Deploy the SMACK stack on DC/OS using Universe packages."""

    service = Service(self.config, self.options)
    service.create()
    service.connect()

    try:
      self.management()
    except:
      self.logger.warning("FIXME: Creating management application failed, assuming it already exists - this is not a good assumption, need better error checking")

    if self.args["--remove"]:
      return "FIXME: We do not currently support removing of the SMACK stack"
    
    self.dcos_package_install("cassandra")
    self.dcos_package_install("kafka")
    self.dcos_package_install("spark")

  def microscaling(self):
    """Deploy or remove a multiocntianer application which demonstrates
    microscaling of individual containers in response to workload.

    """
    try:
      self.management()
    except:
      self.logger.warning("FIXME: Creating management application failed, assuming it already exists - this is not a good assumption, need better error checking")
      
    args = self.args
    args["--app-config"] = "/src/config/demo/microscaling/marathon.json"

    app = App(self.config, self.options)
    app.args = args

    if self.args["--remove"]:
      return app.remove()
    
    print(acs.cli.login(self.config))

    service = Service(self.config, self.options)
    service.create()
    service.connect()

    lb = Lb(self.config, self.options)
    lb.args = self.args
    lb.args["--port"] = 5555
    lb.open()

    timestamp = int(round(time.time() * 1000))
    name = "demo" + str(timestamp)
    storage = Storage(self.config)
    key = storage.create(name)

    # FIXME: workaround incorrect ports in ACS
    self.workaroundBrokenProbes()
    
    tokens = {}
    tokens["AZURE_STORAGE_QUEUE_NAME"] = "microscalingdemoqueue"
    tokens["AZURE_STORAGE_SUMMARY_TABLE_NAME"] = "microscalingdemotable"
    tokens["AZURE_STORAGE_ACCOUNT_NAME"] = name
    tokens["AZURE_STORAGE_ACCOUNT_KEY"] = key
    tokens["SLACK_WEBHOOK"] = "https://hooks.slack.com/services/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"

    service = Service(self.config, self.options)
    service.create()
    service.connect()
    service.install_dcos_cli()

    self.dcos_package_install("marathon-lb")

    return app.deploy(tokens)

  def management(self):
    """Deploy or remove a master proxy that allows (insecure) access to
       the DC/OS UI through http://AGENTS_FQDN:8080

    """
    args = self.args
    args["--app-config"] = "/src/config/demo/management/marathon.json"

    app = App(self.config, self.options)
    app.args = args

    if self.args["--remove"]:
      return app.remove()
    
    print(acs.cli.login(self.config))

    service = Service(self.config, self.options)
    service.create()
    service.connect()

    return app.deploy()
  
  def workaroundBrokenProbes(self):
    """At the time of writing Sept 12 2016 ACS creates the probe for port
    80 and 8080 as TCP probes, they should be HTTP. This method is
    used to workaround this. Once it is fixed in the ACS RP we will
    no longer need to do this.
    
    """

    self.logger.warn("FIXME: working around incorrectly configured probes in ACS")
    rg = self.config.get("Group", "name")
    
    # Get Public Agent LB name
    output, errors = self.utils.shell_execute("azure network lb list " + rg +  " --json")
    lbs = json.loads(output)
    for lb in lbs:
      id = lb["id"]
      if (id.find("-agent-lb-") >= 0):
        lb_name = lb["name"]
        cluster_id = lb_name[-8:]

    command = "azure network lb probe set --protocol http --path / " + rg + " " + lb_name + " tcpHTTPProbe"
    self.utils.shell_execute(command)
      
    command = "azure network lb probe set --protocol http --path / " + rg + " " + lb_name + " tcpPort8080Probe"
    self.utils.shell_execute(command)
