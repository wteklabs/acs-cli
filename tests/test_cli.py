"""tests for the main acs CLI module"""

from acs import __version__ as VERSION

from subprocess import check_output
import pytest

class TestCLI():
    def test_returns_usage_information(self):
        output = check_output(['acs', '-h'])
        assert 'Usage:' in output.decode("utf-8")

        output = check_output(['acs', '--help'])
        assert 'Usage:' in output.decode("utf-8")

    def test_returns_version_informatio(self):
        output = check_output(['acs', '--version'])
        assert output.strip().decode("utf-8") == VERSION
