"""Tests for `acs afs` subcommand."""

import pytest

class TestAfs():

    slow = pytest.mark.skipif(
        not pytest.config.getoption("--runslow"),
        reason="need --runslow option to run"
    )

    @slow
    def test_install(self, afs):
        result = afs.install()
        assert "Exception" not in result

