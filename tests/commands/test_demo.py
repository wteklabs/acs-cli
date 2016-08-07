"""Tests for `acs demo` subcommand."""

import pytest

class TestDemo():
    slow = pytest.mark.skipif(
        not pytest.config.getoption("--runslow"),
        reason="need --runslow option to run"
    )

    def test_lbweb(self, demo):
        demo.args = {'<command>': 'lbweb',
                     "--remove": False}
        try:
            result = demo.lbweb()
            assert("Application deployed" in result)
        except RuntimeWarning as e:
            demo.log.warning("The application was already installed so the test was not as thorough as it could have been")

        
        # remove the appliction
        demo.args["--remove"] = True
        result = demo.lbweb()
        assert("Application removed" in result)
