"""Tests for `service` subcommand."""

import pytest

class TestAfs():

    slow = pytest.mark.skipif(
        not pytest.config.getoption("--runslow"),
        reason="need --runslow option to run"
    )

    def test_deployment(self, service):
        response = service.marathonCommand('apps')
        assert '{"apps":[]}' in response

        with open ('marathon-app.json', "r") as marathonfile:
            data=marathonfile.read().replace('\n', '').replace("\"", "\\\"")
        response = service.marathonCommand('groups', 'POST', data)

        url = "http://" + service.getAgentsFQDN()

        for i in range (0,10):
            self.log.debug("Attempt to access service " + str(i) + " of 10")
            try:
                r = requests.get(url)
                if r.status_code == 200:
                    self.log.debug("Got a 200 response from the application")
                    break
            except:
                e = sys.exc_info()[0]
                self.log.debug("Attempt failed: " + str(e))
                self.log.debug("Sleeping for 5 seconds")
                time.sleep (5)

        assert i >= 9

        service.marathonCommand('groups/azure?force=true', 'DELETE')
        response = service.marathonCommand('apps')
        assert '{"apps":[]}' in response
