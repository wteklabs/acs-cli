"""Tests for `acs service` command."""

import pytest

class TestService():

    slow = pytest.mark.skipif(
        not pytest.config.getoption("--runslow"),
        reason="need --runslow option to run"
    )

    def test_exists(self, service):
        exists = service.exists()
        assert exists

    def test_show(self, service):
        result = service.show()
        assert "rgacstestdcos" in result
        assert "azure.com" in result

