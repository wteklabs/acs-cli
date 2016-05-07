"""Tests for `acs afs` subcommand."""

from subprocess import check_output
from unittest import TestCase
from json import dumps

class TestAfs(TestCase):
    def setUp(self):
        self.BASE_COMMAND = ['acs', 'afs']

# This test takes a long time to run and thus is excluded for now
#    def test_install(self):
#        output = self._execute(['install'])
#        self.assertTrue(len(output) >=  1)

    def _execute(self, command):
        full_cmd = self.BASE_COMMAND
        full_cmd.extend(command)
        result = check_output(full_cmd)
        return result.decode("utf-8")

