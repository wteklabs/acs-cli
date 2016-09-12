"""
Helper for running DCOS CLI commands.
"""
from acs.AcsUtils import AcsUtils

import subprocess, os

class Dcos():
    def __init__(self, acs):
        self.utils = AcsUtils()
        self.acs = acs
        self.logger = self.utils.getLogger("acs.dcos")
        self.utils.shell_execute('. /src/bin/env-setup')
        
    def execute(self, cmd):
        """Execute a DCOS command. Return a tuple containing stdout and
stderr.

        service is the intended recipient ACS instance for the command.

        """
        self.acs.connect()
        output, errors = self.utils.shell_execute("dcos " + cmd)
        self.acs.disconnect()
        
        if errors is not None:
            if 'Missing required config parameter: "core.dcos_url"' in errors:
                self.logger.error("DC/OS CLI is installed, but core.dcos_url is not set. This indicates an incomplete installation of DCOS. In most cases this means that the environment has not been setup, so lets try to fix it.")
                self.execute(cmd)
            else:
                self.logger.error("Unrecoverable error in DCOS CLI:\n" + errors)
            
        self.logger.debug("Output of command:\n" + output)

        return output, errors

    def install_cli(self):
        """ Install the CLI to connect to the indicated service """
        self.logger.info("Installing DCOS CLI")

        self.acs.connect()
    
        cmd = "pip install virtualenv"
        output, errors = self.utils.shell_execute(cmd)

        cmd = "wget https://raw.githubusercontent.com/mesosphere/dcos-cli/master/bin/install/install-optout-dcos-cli.sh -O install-optout-dcos-cli.sh"
        os.system(cmd)

        cmd = "chmod +x install-optout-dcos-cli.sh"
        os.system(cmd)

        cmd = "./install-optout-dcos-cli.sh . http://localhost --add-path yes"
        os.system(cmd)

        self.acs.disconnect()

        self.logger.info("DCOS installed. If you want to use the DC/OS command line directly then execute `. /src/bin/env-setup`")
