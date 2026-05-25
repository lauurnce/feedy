import pytest
from feedy.sources.meta import MetaSource


@pytest.fixture
def source():
    return MetaSource()


def test_source_name(source):
    assert source.name == "meta"
