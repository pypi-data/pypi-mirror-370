import pytest


@pytest.fixture(scope="session")
def fixture_dir(test_dir):
    return test_dir / "fixtures"


@pytest.fixture(scope="session")
def test_dir(pytestconfig):
    return pytestconfig.rootdir / "tests"
