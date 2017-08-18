"""Utilities for sharing across the CLI application.

FIXME: how much of this is actually used now? We seem to have moved
away from this class a fair amount. Looks like only the shell_execute
function is used at present. So I've killed it all to see what breaks.

"""

import logging
import os
import subprocess


class AcsUtils:
    def __init__(self):
        self.logger = self.getLogger("acs.AcsUtils")

    def shell_execute(self, cmd):
        """ Execute a command on the client in a bash shell. 

        Return a tuple of output, errors
        """
        self.logger.debug("Executing command in shell: " + str(cmd))

        dcos_config = os.path.expanduser('~/.dcos/dcos.toml')
        os.environ['PATH'] = ':'.join([os.getenv('PATH'), '/src/bin'])
        os.environ['DCOS_CONFIG'] = dcos_config
        os.makedirs(os.path.dirname(dcos_config), exist_ok=True)

        try:
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE, shell=True)
            output, errors = p.communicate()
        except OSError as e:
            self.logger.error("Error executing command " + str(cmd) + ". " + e)
            raise e

        self.logger.debug("Output of command:\n" + output.decode("utf-8"))
        return output.decode("utf-8"), errors.decode("utf-8")

    def getLogger(self, name):
        """
        Initialize the logger and return it.
        """
        output_dir = os.path.expanduser('~/.acs/logs')
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)

        if (not logger.handlers):
            # create console handler and set level to debug
            handler = logging.StreamHandler()
            handler.setLevel(logging.DEBUG)
            formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - %(name)s : %(lineno)d in %(filename)s : %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)

            # create error file handler and set level to error
            handler = logging.FileHandler(os.path.join(output_dir, "error.log"),
                                          "w", encoding=None, delay="true")
            handler.setLevel(logging.ERROR)
            formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - %(name)s : %(lineno)d in %(filename)s : %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)

            # create debug file handler and set level to debug
            handler = logging.FileHandler(os.path.join(output_dir, "all.log"),
                                          "w")
            handler.setLevel(logging.DEBUG)
            formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - %(name)s : %(lineno)d in %(filename)s : %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)

            logger.debug("Logs being written to " + output_dir)

        return logger
