from feedy.cli import _build_sources
from feedy.sources.hackernews import HackerNewsSource


def test_build_sources_instantiates_known_names():
    sources = _build_sources(["hackernews"])
    assert len(sources) == 1
    assert isinstance(sources[0], HackerNewsSource)
