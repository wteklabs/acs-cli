"""
acs

Usage:
  acs [--config-file=<file>] [--version] [--help] <command> [<args>...]

Options: 
  -h --help                           Show this help.

Commands:
  login      Login to Azure interactively
  service    Create and manage Azure Container Service
  app        Deploy and manage applications in the cluster
  lb         Manage the Agents load balancer
  demo       Setup demo environments easily
  docker     Send docker commands to a Docker Swarm cluster
  afs        Add the Azure Files Docker volume driver to each agent
  oms        Add or configure Operational Management Suite monitoring

See `acs <command> --help` for information on a specific command.

Help:
  For help using this tool please open an issue on the GitHub repository:
  https://github.com/rgardler/acs-scripts
"""

import subprocess
from inspect import getmembers, isclass

from docopt import docopt

from acs.acs import Config
from .AcsUtils import AcsUtils
from . import __version__ as VERSION


def main():
    """Main CLI entrypoint"""
    from . import commands

    args = docopt(__doc__, version=VERSION, options_first=True)

    config = Config(args['--config-file'])
    command_name = args["<command>"]
    if command_name == "login":
        print(login(config))
        return

    argv = args['<args>']
    module = getattr(commands, command_name)
    commands = getmembers(module, isclass)
    command_class = None
    command = None
    for k, command_class in commands:
        if command_name.lower() in command_class.__name__.lower():
            command = command_class(config, argv)
    if command is None:
        raise Exception("Unrecognized command: " + command_name)
    command.run()


def login(config):
    p = subprocess.Popen(["azure", "account", "show"], stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    output, errors = p.communicate()
    if errors:
        # Not currently logged in

        utils = AcsUtils()
        output, errors = utils.shell_execute("azure login")
        if errors:
            return "Failed to login: " + errors

        id = config.get('Azure', 'SubscriptionID')
        output, errors = utils.shell_execute("azure login")
        if errors:
            return "Failed to switch to subscription defined in config.py: " + errors
        else:
            return "Logged in to Azure subscription id: " + id
