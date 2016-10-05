"""Tests for `acs service` command."""

from acs.AgentPool import AgentPool

import pytest
import time
import urllib.request

class TestService():

    max_deploy_time = 25 # minutes

    slow = pytest.mark.skipif(
        not pytest.config.getoption("--runslow"),
        reason="need --runslow option to run"
    )

    @slow
    def test_create(self, service):
        if service.exists():
            service.logger.debug("The test ACS cluster already exists, deleting")
            service.delete(True)
        exists = service.exists()
        assert not exists

        starttime = time.time()
        service.create()
        assert service.exists()
        endtime = time.time()
        service.logger.info("Total deployment time: " + str((endtime - starttime)/60) + " minutes")

        dns_up = False
        start_time = time.time()
        duration = 0
        while not dns_up and duration < (2 * 60):
            dns_up = service.exists()
            duration = time.time() - start_time
        assert dns_up, "DNS for the masters did not seem to come up"
            
    def test_exists(self, service):
        exists = service.exists()
        assert exists

    def test_show(self, service):
        result = service.show()
        assert "rgDcosTest" in result
        assert "azure.com" in result

    def test_connect(self, service):
        results = service.connect()

        isConnected = False
        req = urllib.request.Request("http://localhost")
        with urllib.request.urlopen(req) as response:
            html = response.read()
            isConnected = True
        assert(isConnected)

        service.disconnect()

    def test_disconnect(self, service):
        results = service.connect()
        isConnected = True
        
        results = service.disconnect()
        req = urllib.request.Request("http://localhost")
        try:
            with urllib.request.urlopen(req) as response:
                html = response.read()
                isConnected = True
        except urllib.error.URLError as e:
            isConnected = False
        assert(not isConnected)
        
    @slow
    def test_scale(self, service, agentPool):
        initial_agents_count = service.config.getint('ACS', 'agentCount')
        service.args = {'--agents': initial_agents_count + 1}

        result = service.scale()

        final_agent_count = agentPool.getAgentCount()
        # test for >= because of overprovisioning
        assert final_agent_count >= initial_agents_count + 1

    @slow
    def test_deallocate_and_restart(self, service):
        service_up = False
        start_time = time.time()
        duration = 0
        while not service_up and duration < (2 * 60):
            service_up = service.exists()
            duration = time.time() - start_time
        assert service_up, "DNS for the masters did not seem to come up"

        service.deallocate()

        service_up = False
        start_time = time.time()
        duration = 0
        while not service_up and duration < (1 * 60):
            service_up = service.exists()
            duration = time.time() - start_time
        assert not service_up, "We don't seem to have deallocated"

        service.start()

        service_up = False
        start_time = time.time()
        duration = 0
        while not service_up and duration < (2 * 60):
            service_up = service.exists()
            duration = time.time() - start_time
        assert service_up, "We don't seem to have restarted"
