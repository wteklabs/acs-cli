"""Tests for `acs afs` subcommand."""

import pytest

class TestAfs():

    slow = pytest.mark.skipif(
        not pytest.config.getoption("--runslow"),
        reason="need --runslow option to run"
    )

    def test_deployment(self, service):
        response = service.marathonCommand('apps')
        assert '{"apps":[]}' in response
