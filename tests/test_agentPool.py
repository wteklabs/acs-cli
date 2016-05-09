from acs import __version__ as VERSION

import pytest

class TestAgentPool():
    def test_getPools(self, agentPool):
        pools = agentPool.getPools()
        num_pools = len(pools)
        assert num_pools == 2

    def test_getAgents(self, agentPool):
        agents = agentPool.getAgents();
        num_agents = len(agents)
        assert num_agents == 5

    def test_getNICs(self, agentPool):
        nics = agentPool.getNICs();
        num_nics = len(nics)
        assert num_nics == 5
