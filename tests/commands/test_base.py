"""Tests the base command class."""

import pytest
import re

class TestConfig():
    def test_get_cluster_setup(self, base):
        setup = base.getClusterSetup()
        assert re.match(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}",setup['masters']['ip']), "There is no IP address associated with the Masters Load Balancer"
