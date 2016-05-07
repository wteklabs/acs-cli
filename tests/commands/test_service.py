"""Tests for `acs service` command."""

from acs import commands
from acs.commands.base import Config

import pytest

class TestService():

    slow = pytest.mark.skipif(
        not pytest.config.getoption("--runslow"),
        reason="need --runslow option to run"
    )

    @slow
    def test_create(self, service):
        result = service.create()
        assert "foo" in result

    def test_show(self, service):
        result = service.show()
        assert "rgacstestdcos" in result
        assert "azure.com" in result

    @pytest.fixture
    def service(self):
        config = Config("tests/test_dcos_cluster.ini")
        return commands.Service(config, None)
