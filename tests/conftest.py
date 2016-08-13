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
def afs(service):
    return commands.Afs(config(), None)

@pytest.fixture(scope="module")
def demo(service):
    return commands.Demo(config(), None)

@pytest.fixture(scope="module")
def lb(service):
    return commands.Lb(config(), None)

@pytest.fixture(scope="module")
def oms(service):
    return commands.Oms(config(), None)

@pytest.fixture(scope="module")
def service():
    service = commands.Service(config(), None)
    
    if not service.exists():
        service.logger.debug("The test ACS cluster does not exist, creating")
        service.create()

    assert service.exists()
    
    return service

@pytest.fixture(scope="module")
def agentPool(service):
    return AgentPool(config())

@pytest.fixture(scope="module")
def config():
    return Config("tests/test_dcos_cluster.ini")
