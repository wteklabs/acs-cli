"""The base command class. All implemented commands should extend this class."""
from ..AgentPool import AgentPool
from ..AcsUtils import AcsUtils
from ..acs import Acs
import json
import os.path
from subprocess import call
import paramiko
from paramiko import SSHClient
from paramiko.agent import AgentRequestHandler
import socket
import subprocess, os


class Base(object):
    temp_filepath = os.path.expanduser("~/.acs/tmp")

    def __init__(self, config, options, *args, **kwargs):
        self.utils = AcsUtils()
        self.acs = Acs(config)
        self.logger = self.utils.getLogger("acs.command.base")
        self.config = config
        self.options = options
        self.args = args
        self.kwargs = kwargs
        os.makedirs(self.temp_filepath, exist_ok=True)
        self.login()

    def login(self):
        p = subprocess.Popen(["azure", "account", "show"],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, errors = p.communicate()
        if errors:
            # Not currently logged in

            p = subprocess.Popen(["azure", "login"], stderr=subprocess.PIPE)
            output, errors = p.communicate()
            if errors:
                return "Failed to login: " + errors.decode("utf-8")
            return "Logged in to Azure"

    def getManagementEndpoint(self):
        """ DEPRECATED: 1.1.2 """
        return self.acs.getManagementEndpoint()

    def getAgentEndpoint(self):
        """ DEPRECATED: 1.1.2 """
        return self.acs.getAgentEndpoint()

    def createResourceGroup(self):
        """ DEPRECATED: 1.1.2 """
        self.acs.createResourceGroup()

    def run(self):
        raise NotImplementedError(
            "You must implement the run() method in your commands")

    def help(self):
        raise NotImplementedError(
            "You must implement the help method. In most cases you will simply do 'print(__doc__)'")

    def getAgentIPs(self):
        """ DEPRECATED: 1.1.2 """
        return self.acs.getAgentIPs()

    def executeOnAgent(self, cmd, ip):
        """ DEPRECATED: 1.1.2 """
        return self.acs.executeOnAgent(cmd, ip)

    def executeOnMaster(self, cmd):
        """ DEPRECATED: 1.1.2 """
        return self.acs.executeOnmaster(cmd)

    def getClusterSetup(self):
        """ DEPRECATED: 1.1.2 """
        return self.acs.getClusterSetup()

    def shell_execute(self, cmd):
        """ DEPRECATED: since 1.1.2 use AcsUtils.shell_execute() instead"""
        self.utils.shell_execute(cmd)
