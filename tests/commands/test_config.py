"""TEsts for the cluster.ini and config class."""

import os
import pytest

class TestConfig():

    slow = pytest.mark.skipif(
        not pytest.config.getoption("--runslow"),
        reason="need --runslow option to run"
    )

    def test_generateSSHKey(self, config):
        public_filepath = '~/.ssh/acs_cli_test.pub'
        private_filepath = '~/.ssh/acs_cli_test'

        try:
            os.remove(os.path.expanduser(public_filepath))
            os.remove(os.path.expanduser(private_filepath))
        except:
            # Assume that this failed because it doesn't exist
            pass

        config._generateSSHKey(private_filepath, public_filepath)
        
        assert os.path.isfile(os.path.expanduser(private_filepath))
        assert os.path.isfile(os.path.expanduser(public_filepath))

    def test_get_ssh_keys(self, config):
        public_key = config.get("SSH", "publickey")
        private_key = config.get("SSH", "privateKey")
        public_file = os.path.expanduser(config.config_parser.get('SSH', 'publicKey'))
        private_file = os.path.expanduser(config.config_parser.get('SSH', 'privatekey'))

        with open(private_file, 'r') as sshfile: 
            key = sshfile.read().replace('\n', '') 
        assert key == private_key

        with open(public_file, 'r') as sshfile: 
            key = sshfile.read().replace('\n', '') 
        assert key == public_key
