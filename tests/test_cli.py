"""tests for the main acs CLI module"""

from subprocess import check_output
from unittest import TestCase

from acs import __version__ as VERSION

class TestHelp(TestCase):
    def test_returns_usage_information(self):
        output = check_output(['acs', '-h'])
        self.assertTrue('Usage:' in output.decode("utf-8"))

        output = check_output(['acs', '--help'])
        self.assertTrue('Usage:' in output.decode("utf-8"))

class TestVersion(TestCase):
    def test_returns_version_informatio(self):
        output = check_output(['acs', '--version'])
        self.assertEqual(output.strip().decode("utf-8"), VERSION)
