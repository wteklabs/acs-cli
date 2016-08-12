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
        expected_agents = agentPool.getAgentCount()
        assert num_agents == expected_agents

    def test_getAgentCount(self, agentPool, config):
        agent_count = agentPool.getAgentCount()
        private_pool_size = 3
        expected_count = int(config.get("ACS", "agentCount")) + private_pool_size
        assert expected_count == agent_count
