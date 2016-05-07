"""Tests for `acs service` command."""

from subprocess import check_output
from unittest import TestCase

class TestService(TestCase):

# Thia test is very slow, so we are not running it right now
#    def test_create_exits_succesfully(self):
#        output = self.execute(['acs', 'service', 'create'])
#        pass

    def test_show(self):
        output = self._execute(['acs', 'service', 'show'])
        self.assertTrue("azure.com" in output)

    def _execute(self, command):
        result = check_output(command)
        return result.decode("utf-8")
