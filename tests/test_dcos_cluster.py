"""Tests for `service` subcommand."""

import pytest
import sys
import time

class TestDCOS():

    slow = pytest.mark.skipif(
        not pytest.config.getoption("--runslow"),
        reason="need --runslow option to run"
    )

    @slow
    def test_deployment(self, service):
        with open ('marathon-app.json', "r") as marathonfile:
            data=marathonfile.read().replace('\n', '').replace("\"", "\\\"")
        response = service.marathonCommand('groups', 'POST', data)

        url = "http://" + service.getAgentEndpoint()

        for i in range (0,10):
            try:
                r = requests.get(url)
                if r.status_code == 200:
                    break
            except:
                e = sys.exc_info()[0]
                time.sleep(5)

        assert i >= 9

