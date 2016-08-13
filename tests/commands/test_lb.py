"""Tests for `acs lb` subcommand."""

from subprocess import check_output
import time

import pytest

class TestLb():
    slow = pytest.mark.skipif(
        not pytest.config.getoption("--runslow"),
        reason="need --runslow option to run"
    )

    @slow
    def test_open(self, lb):
        starttime = time.time()
        lb.args = {'--port': '32123'}
        
        result = lb.open()
        endtime = time.time()

        lb.logger.info("Total time to open port: " + str((endtime - starttime)/60) + " minutes")
        
        assert('Opened port 32123' in result)

