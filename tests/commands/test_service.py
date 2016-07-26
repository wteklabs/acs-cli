"""Tests for `acs service` command."""

from acs.AgentPool import AgentPool

import pytest
import time

class TestService():

    max_deploy_time = 25 # minutes

    slow = pytest.mark.skipif(
        not pytest.config.getoption("--runslow"),
        reason="need --runslow option to run"
    )

    @slow
    def test_create(self, service):
        if service.exists():
            service.log.debug("The test ACS cluster already exists, deleting")
            service.delete(True)
        exists = service.exists()
        assert not exists

        starttime = time.time()
        service.create()
        assert service.exists()
        endtime = time.time()
        service.log.info("Total deployment time: " + str((endtime - starttime)/60) + " minutes")

        dns_up = False
        start_time = time.time()
        duration = 0
        while not dns_up and duration < (2 * 60):
            dns_up = service.exists()
            duration- time.time() - start_time
        assert dns_up, "DNS for the masters did not seem to come up"
            
    def test_exists(self, service):
        exists = service.exists()
        assert exists

    def test_show(self, service):
        result = service.show()
        assert "rgDcosTest" in result
        assert "azure.com" in result

    @slow
    def test_scale(self, service):
        initial_agents = service.config.getint('ACS', 'agentCount')
        service.args = {'--agents': initial_agents + 1}

        result = service.scale()
        assert "Scaled to " + str(initial_agents + 1) == result
