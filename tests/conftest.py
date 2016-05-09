import pytest

from acs import commands
from acs.commands.base import Config

def pytest_addoption(parser):
    parser.addoption("--runslow", action="store_true",
        help="run slow tests")

@pytest.fixture(scope="module")
def afs():
    config = Config("tests/test_dcos_cluster.ini")
    return commands.Afs(config, None)

@pytest.fixture(scope="module")
def oms():
    config = Config("tests/test_dcos_cluster.ini")
    return commands.Oms(config, None)

@pytest.fixture(scope="module")
def service():
    config = Config("tests/test_dcos_cluster.ini")
    return commands.Service(config, None)
