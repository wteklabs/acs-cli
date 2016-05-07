"""Tests for `acs service` command."""

from subprocess import check_output
from acs import commands
from acs.commands.base import Config

import pytest

class TestService():

# Thia test is very slow, so we are not running it right now
#    def test_create_exits_succesfully(self):
#        output = self.execute(['acs', 'service', 'create'])
#        pass

    def test_show(self, service):
        result = service.show()
        assert "rgacstestdcos" in result
        assert "azure.com" in result

    @pytest.fixture
    def service(self):
        config = Config("tests/test_dcos_cluster.ini")
        return commands.Service(config, None)
