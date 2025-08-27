# Contributing to feedy

Thanks for your interest in improving `feedy`! This guide covers the dev setup,
project conventions, and how to add a new feed source.

## Development setup

Requires Python 3.11+.

```bash
git clone https://github.com/<your-account>/feedy.git
cd feedy
pip install -e ".[dev]"
pytest
```

All changes should keep the test suite green. We work test-first: write a
failing test, then the code that makes it pass.

## Project layout

```
feedy/
├── feedy/
│   ├── sources/        # one module per feed source
│   │   └── base.py     # BaseFeedSource ABC + FeedEntry schema
│   ├── storage.py      # SQLite save / dedup / query
│   ├── summarizer.py   # turns entries into AI summaries
│   ├── digest.py       # groups + formats entries
│   ├── config.py       # ~/.feedy/config.toml loader
│   ├── ai.py           # Anthropic API wrapper
│   └── cli.py          # Click commands: fetch / list / digest
└── tests/              # pytest, one test_*.py per module
```

## Adding a new source in ~10 lines

A source subclasses `BaseFeedSource` and implements three methods: `fetch`
(get raw data), `parse` (extract intermediate dicts), and `to_dict` (normalise
to the `FeedEntry` schema). The base class's `run()` chains them and drops
entries missing a URL or title.

Here's a complete source for a hypothetical JSON API:

```python
# feedy/sources/example.py
import httpx
from feedy.sources.base import BaseFeedSource, FeedEntry


class ExampleSource(BaseFeedSource):
    name = "example"

    def fetch(self):
        return httpx.get("https://example.com/blog.json", timeout=10).json()

    def parse(self, raw):
        return raw["posts"]

    def to_dict(self, entry):
        return FeedEntry(url=entry["link"], title=entry["headline"],
                         date=entry["published"], source=self.name, summary="")
```

> `name` can be a plain class attribute (as above) or a `@property` — see the
> existing sources for the property style. Scraping sources use
> `BeautifulSoup` in `parse`; look at `feedy/sources/hackernews.py` for a
> worked HTML example.

### Wire it up

1. Register the class in the CLI registry in `feedy/cli.py`:

   ```python
   from feedy.sources.example import ExampleSource

   registry = {
       ...
       "example": ExampleSource,
   }
   ```

2. Add `"example"` to `DEFAULT_SOURCES` in `feedy/config.py` if it should be
   enabled by default.

3. Add a `tests/test_example.py` covering `parse` and `to_dict` against a
   saved sample of the source's response (no live network in tests).

4. Add a row to the Sources table in `README.md`.

## Submitting changes

1. Branch off `main`.
2. Make your change with tests; run `pytest`.
3. Use clear commit messages (this repo uses Conventional Commits, e.g.
   `feat(sources): add ExampleSource`).
4. Open a pull request describing what and why.

- Land the failing test in its own commit before the implementation that satisfies it.
- Prefix commits with a type and a module scope, e.g. `feat(storage):`.
- Run `make test` before pushing; the suite is offline and takes seconds.
- Keep one logical change per commit; if the message needs "and", split it.
- Document new public functions with a one-line docstring in the same commit.
- Update `CHANGELOG.md` under Unreleased when behaviour changes.
