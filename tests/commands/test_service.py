"""Tests for `acs service` command."""

from acs.AgentPool import AgentPool

import pytest

class TestService():

    slow = pytest.mark.skipif(
        not pytest.config.getoption("--runslow"),
        reason="need --runslow option to run"
    )

    def test_exists(self, service):
        exists = service.exists()
        assert exists

    def test_show(self, service):
        result = service.show()
        assert "rgacstestdcos" in result
        assert "azure.com" in result

    def test_scale(self, service):
        initial_agents = service.config.getint('ACS', 'agentCount')
        service.args = {'--agents': initial_agents + 1}

        result = service.scale()
        assert "Scaled to " + str(initial_agents + 1) == result
