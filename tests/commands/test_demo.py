"""Tests for `acs demo` subcommand."""

import pytest
import urllib.request

class TestDemo():
    slow = pytest.mark.skipif(
        not pytest.config.getoption("--runslow"),
        reason="need --runslow option to run"
    )

    def test_lbweb(self, demo, service):
        """Tests the creation of the lbweb demo. This version of the test will fail if the test cluster dows not already exist.

        """
        assert(service.exists())

        demo.args = {'<command>': 'lbweb',
                     "--remove": False}
        try:
            result = demo.lbweb()
            assert("Application deployed" in result)
            assert(self.isSimpleWebUp(service))
        except RuntimeWarning as e:
            demo.logger.warning("The application was already installed so the test was not as thorough as it could have been")
        
        # remove the appliction
        demo.args["--remove"] = True
        result = demo.lbweb()
        assert("Application removed" in result)


    def isSimpleWebUp(self, service):
        isConnected = False
        attempts = 0
        while not isConnected and attempts < 50:
          req = urllib.request.Request("http://" + service.getAgentEndpoint())
          try:
            with urllib.request.urlopen(req) as response:
              html = response.read()
              if "Real Visit Results" in html:
                  isConnected = True
          except urllib.error.URLError as e:
            isConnected = False
            attempts = attempts + 1
            time.sleep(0.1)
