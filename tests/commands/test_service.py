"""Tests for `acs service` command."""

from subprocess import check_output
from unittest import TestCase

class TestService(TestCase):
    def test_create_exits_succesfully(self):
        output = self.execute(['acs', 'service', 'create'])
        pass

    def execute(self, command):
        result = check_output(command)
        return result.decode("utf-8")
