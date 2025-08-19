import pytest


def pytest_addoption(parser):
    parser.addoption("--location", action="store", default="eastus2euap")


@pytest.fixture
def location(request):
    return request.config.getoption("--location")
