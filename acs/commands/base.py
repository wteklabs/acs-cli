"""The base command class. All implemented commands should extend this class."""

class Base(object):

  def __init__(self, options, *args, **kwargs):
    self.options = options
    self.args = args
    self.kwargs = kwargs

  def run(self):
    raise NotImplementedError("You must implement the run() method in your commands")

  def print_help(self):
    raise NotImplementedError("You must implement the print_help method. In most cases you will simply do 'print(__doc__)'")
