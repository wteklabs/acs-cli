""" 

Manage Agent load balancer.

Usage:
  lb <command> [help] [options]

Commands:
  open     open a port  

Options:
  --port=<number>            the port to operate upon
  --protocol=<tcp_or_http>   the protocol to probe on [DEFAULT 'http']

Help:
  For help using the oms command please open an issue at 
  https://github.com/rgardler/acs-scripts
"""

from docopt import docopt
from inspect import getmembers, ismethod
import json
import os
import subprocess as sub
import time

from .base import Base

class Lb(Base):

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

  def open(self):
    port = self.args["--port"]
    if not port:
      self.logger.error("Attempt to open an LB port without specifying '--port'")
      return "Specify the port number with '--port'"

    if "--protocol" in self.args:
      protocol = self.args["--protocol"]
      if not (protocol == "http" or protocol == "tcp"):
        msg = "Protocol must be wither 'tcp' or 'http'"
        self.logger.error("Invavlid prorotocol provided " + msg)
        return msg
    else:
      protocol = "http"
      
    # TODO: allow path to be configured on the command line
    path = '/'

    base_name = "acsPort"
    probe_name = base_name + "Probe" + str(port)
    rule_name= base_name + "LbRule" + str(port)
    nsg_rule_name = base_name + "NsgRule" + str(port)
    rg = self.config.get("Group", "name")

    # List the LBs in order to get the name of the public agent LB
    cmd = "azure network lb list " + rg + " --json"
    output, errors = self.utils.shell_execute(cmd)
    lbs = json.loads(output)
    for lb in lbs:
      id = lb["id"]
      if (id.find("-agent-lb-") >= 0):
        lb_name = lb["name"]
        self.logger.debug("Agent load balancer name is " + lb_name)
        cluster_id = lb_name[-8:]
        self.logger.debug("Cluster ID " + cluster_id)

    # Create a probe
    if protocol == "http":
      p = sub.Popen(['azure', 'network', 'lb', 'probe', "create", "-o", str(port), "-p", protocol, "-f", path, "-g", rg, "-l", lb_name, "-n", probe_name],stdout=sub.PIPE,stderr=sub.PIPE)
    else:
      p = sub.Popen(['azure', 'network', 'lb', 'probe', "create", "-o", str(port), "-p", protocol, "-g", rg, "-l", lb_name, "-n", probe_name],stdout=sub.PIPE,stderr=sub.PIPE)
            
    output, errors = p.communicate()
    if errors:
      self.logger.error("Error creating probe for LB rule:\n" + errors.decode("utf-8"))
      return "Unable to create probe for LB rule, see log for full details."
    self.logger.debug("Created probe called " + probe_name)
    
    backend_pool = "dcos-agent-pool-" + cluster_id

    # Create an LB rule
    p = sub.Popen(['azure', 'network', 'lb', 'rule', "create", "-g", rg, "-l", lb_name, "-n", rule_name, "-p", "tcp", "-f", str(port), "-b", str(port), "-o", backend_pool, "-a", probe_name],stdout=sub.PIPE,stderr=sub.PIPE)
    output, errors = p.communicate()
    if errors:
      self.logger.error("Error creating LB rule:\n" + errors.decode("utf-8"))
      self.logger.error("TODO: cleanup after failed LB port opening - delete probe that was created")
      return "Unable to create LB rule, see log for full details."
    self.logger.debug("Created LB rule named " + rule_name)
                   
    # Create an NSG Rule
    nsg_name = "dcos-agent-public-nsg-" + cluster_id
    priority = 350
    self.logger.warning("FIXME: Currently nsg rule priority is set at 350, this will clash if we try to setup a second rule")
    p = sub.Popen(['azure', 'network', 'nsg', "rule", "create", "-g", rg, "-a", nsg_name, "-p", "*", "-u", str(port), "-n", nsg_rule_name, "-y", str(priority)],stdout=sub.PIPE,stderr=sub.PIPE)
    output, errors = p.communicate()
    if errors:
      self.logger.error("Error creating NSG rule:\n" + errors.decode("utf-8"))
      self.logger.error("FIXME: cleanup after failed NSG rule creation - delete probe and LB rule that was created")
      return "Unable to create LB rule, see log for full details."
    self.logger.debug("Created NSG rule named " + nsg_rule_name)
    
    self.logger.info("Opened port " + str(port) + " in lb called " + lb_name + " using probe named " + probe_name)
    return "Opened port " + str(port)
