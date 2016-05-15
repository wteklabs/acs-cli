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
        assert num_agents == config.get("ACS", "agentCount")

    def test_getNICs(self, agentPool, config):
        nics = agentPool.getNICs();
        num_nics = len(nics)
        assert num_nics == config.get("ACS", "agentCount")
