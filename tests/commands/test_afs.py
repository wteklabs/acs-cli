"""Tests for `acs afs` subcommand."""

from acs import commands
from acs.commands.base import Config

import pytest

class TestAfs():

    slow = pytest.mark.skipif(
        not pytest.config.getoption("--runslow"),
        reason="need --runslow option to run"
    )

    @slow
    def test_install(self, afs):
        result = afs.install()
        assert "foo" in result

    @pytest.fixture
    def afs(self):
        config = Config("tests/test_dcos_cluster.ini")
        return commands.Afs(config, None)
