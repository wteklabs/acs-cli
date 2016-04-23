"""
acs

Usage:
  acs [--config-file=<file>] [--version] [--help] <command> [<args>...]

Options: 
  -h --help                           Show this screen.

Commands:
  afs        Add the Azure Files Docker volume driver to each agent
  oms        Add or configure Operational Management Suite monitoring

See `acs help <command>` for information on a specific command.

Help:
  For help using this tool please open an issue on the GitHub repository:
  https://github.com/rgardler/acs-scripts
"""

from . import __version__ as VERSION
from acs.acs_utils import *

from docopt import docopt
from inspect import getmembers, isclass
import os.path
import sys

def main():
  """Main CLI entrypoint"""
  from . import commands
  args = docopt(__doc__, version=VERSION, options_first=True)

  print("Global args:")
  print(args)

  config_file = args['--config-file']
  if not config_file:
    config_file = "cluster.ini"
  if os.path.isfile(config_file):
    acs = ACSUtils(config_file)
  else:
    raise Exception("Configuration file '" + config_file + "' not found")

  command_name = args["<command>"]
  argv = args['<args>']
  module = getattr(commands, command_name)
  commands = getmembers(module, isclass)
  command_class = None
  for k, command_class in commands:
      if command_name.lower() in command_class.__name__.lower():
        command = command_class(argv)
  command.run()
