import pytest
from pytest import FixtureRequest

from pytest_respect.ext.jsonyx import jsonyx_compactish_encoder, jsonyx_permissive_loader
from pytest_respect.resources import TestResources

# All these tests need jsonyx
pytestmark = pytest.mark.jsonyx


@pytest.fixture
def resources(request: FixtureRequest) -> TestResources:
    """The fixture being tested."""
    return TestResources(request)


def test_load_json__jsonyx_permissive(resources):
    resources.json_loader = jsonyx_permissive_loader
    data = resources.load_json()
    assert data == {"look": ["what", "I", "found"]}


def test_expected_json__jsonyx(resources):
    resources.json_encoder = jsonyx_compactish_encoder
    resources.expect_json(
        {
            "look": ["what", "I", "found"],
            "numbers": [1, 2, 3, 4],
            "sub": {"simple": 1, "dict": 2, "is": 3, "flat": 4},
        }
    )
