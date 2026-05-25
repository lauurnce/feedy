import pytest
from feedy.sources.tiktok import TikTokSource


@pytest.fixture
def source():
    return TikTokSource()


def test_source_name(source):
    assert source.name == "tiktok"
