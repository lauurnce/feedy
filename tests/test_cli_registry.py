from feedy.cli import _build_sources
from feedy.sources.hackernews import HackerNewsSource


def test_build_sources_instantiates_known_names():
    sources = _build_sources(["hackernews"])
    assert len(sources) == 1
    assert isinstance(sources[0], HackerNewsSource)


def test_build_sources_skips_unregistered_names():
    assert _build_sources(["nope"]) == []


def test_build_sources_preserves_requested_order():
    names = [s.name for s in _build_sources(["openai", "hackernews"])]
    assert names == ["openai", "hackernews"]
