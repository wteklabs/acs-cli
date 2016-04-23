"""Tests for `acs afs` subcommand."""

from subprocess import check_output
from unittest import TestCase
from json import dumps

class TestAfs(TestCase):
    def setUp(self):
        self.BASE_COMMAND = ['acs', 'afs']

    def test_install(self):
        output = self.execute(['install'])
        self.assertTrue(len(output) >=  1)

    def execute(self, command):
        full_cmd = self.BASE_COMMAND
        full_cmd.extend(command)
        result = check_output(full_cmd)
        return result.decode("utf-8")
