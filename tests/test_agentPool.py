from acs import __version__ as VERSION

import pytest

class TestAgentPool():
    def test_getPools(self, agentPool):
        pools = agentPool.getPools()
        num_pools = len(pools)
        assert num_pools == 2

    def test_getAgents(self, agentPool, config):
        agents = agentPool.getAgents();
        num_agents = len(agents)
        expected_agents = int(config.get("ACS", "agentCount"))
        print("expected private agents = " + str(expected_agents))
        if (int(config.get("ACS", "masterCount")) >= 3):
            expected_agents = expected_agents + 3
        else:
            expected_agents = expected_agents + 1
        assert num_agents == expected_agents

    def test_getAgentCount(self, agentPool, config):
        agent_count = agentPool.getAgentCount()
        expected_count = int(config.get("ACS", "agentCount"))
        assert expected_count == agent_count
