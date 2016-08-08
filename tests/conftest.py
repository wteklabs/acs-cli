import pytest

from acs.AgentPool import AgentPool
from acs import commands
from acs.commands.base import Config

def pytest_addoption(parser):
    parser.addoption("--runslow", action="store_true",
        help="run slow tests")

@pytest.fixture(scope="module")
def base():
    config = Config("tests/test_dcos_cluster.ini")
    return commands.Base(config, None)

@pytest.fixture(scope="module")
def afs():
    config = Config("tests/test_dcos_cluster.ini")
    return commands.Afs(config, None)

@pytest.fixture(scope="module")
<<<<<<< HEAD
def demo():
    config = Config("tests/test_dcos_cluster.ini")
    return commands.Demo(config, None)

@pytest.fixture(scope="module")
def lb():
    config = Config("tests/test_dcos_cluster.ini")
    return commands.Lb(config, None)

@pytest.fixture(scope="module")
def oms():
    config = Config("tests/test_dcos_cluster.ini")
    return commands.Oms(config, None)

@pytest.fixture(scope="module")
def service():
    config = Config("tests/test_dcos_cluster.ini")
    return commands.Service(config, None)

@pytest.fixture(scope="module")
def agentPool():
    config = Config("tests/test_dcos_cluster.ini")
    return AgentPool(config)

@pytest.fixture(scope="module")
def config():
    return Config("tests/test_dcos_cluster.ini")
