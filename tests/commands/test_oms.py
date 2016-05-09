"""Tests for `acs oms` subcommand."""

import pytest

class TestOms():

    slow = pytest.mark.skipif(
        not pytest.config.getoption("--runslow"),
        reason="need --runslow option to run"
    )

    @slow
    def test_install(self, oms):
        result = oms.install()
        assert "Exception" not in result
