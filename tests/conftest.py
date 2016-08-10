import pytest

from acs.AgentPool import AgentPool
from acs import commands
from acs.commands.base import Config

def pytest_addoption(parser):
    parser.addoption("--runslow", action="store_true",
        help="run slow tests")

@pytest.fixture(scope="module")
def base():
    return commands.Base(config(), None)

@pytest.fixture(scope="module")
def afs():
    return commands.Afs(config(), None)

@pytest.fixture(scope="module")
def demo():
    return commands.Demo(config(), None)

@pytest.fixture(scope="module")
def lb():
    return commands.Lb(config(), None)

@pytest.fixture(scope="module")
def oms():
    return commands.Oms(config(), None)

@pytest.fixture(scope="module")
def service():
    return commands.Service(config(), None)

@pytest.fixture(scope="module")
def agentPool():
    return AgentPool(config())

@pytest.fixture(scope="module")
def config():
    return Config("tests/test_dcos_cluster.ini")
