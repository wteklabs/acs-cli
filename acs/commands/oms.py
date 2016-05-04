"""
Commands for working with OMS and ACS

Usage:
  oms <command> [help] [options]

Commands:
  hello                A friendly welcoming message

Options:
  -n --name=NAME       Name of person to say hello to.
  --familiar           Whether to use a familiar greeting.

Help:
  For help using the oms command please open an issue at 
  https://github.com/rgardler/acs-scripts
"""

from docopt import docopt
from inspect import getmembers, ismethod
from json import dumps

from .base import Base

class Oms(Base):

  def run(self):
      args = docopt(__doc__, argv=self.options)
      # print("Global args")
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

  def hello(self):
      """
      A simple demo that says hello.
      """
      if self.args['--familiar']:
          greeting = "Hi "
      else:
          greeting = "Hello, "
      name = self.args['--name']
      if name:
          return greeting + name
      else:
          return 'Hello, world!'


  def help(self):
    print(__doc__)
