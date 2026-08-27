# VC News Pipeline - Implementation Plan

## Executive Summary

Expand `feedy` to track news from top-tier US venture capital firms and accelerators. This will enable users to get AI-summarized digests of VC firm announcements, portfolio news, partner perspectives, and industry insights.

## Target Firms & Sources

### Tier 1 - Mega Funds (Priority 1)

| Firm | Source Name | Content URL | Type | RSS/Feed |
|------|-------------|-------------|------|----------|
| Sequoia Capital | `sequoia` | https://sequoiacap.com/stories | Blog/News | https://sequoiacap.com/feed/ (check) |
| Sequoia Capital | `sequoia-inference` | https://inferencebysequoia.substack.com | Substack | https://inferencebysequoia.substack.com/feed |
| Andreessen Horowitz (a16z) | `a16z` | https://a16z.com/news-content/ | Blog/News | https://a16z.com/feed/ (check) |
| Andreessen Horowitz (a16z) | `a16z-substack` | https://www.a16z.news | Substack | https://www.a16z.news/feed |
| Y Combinator | `ycombinator` | https://www.ycombinator.com/blog | Blog | https://www.ycombinator.com/blog/feed |
| First Round Capital | `firstround` | https://review.firstround.com | Blog/Review | https://review.firstround.com/feed |
| First Round Capital | `firstround-news` | https://www.firstround.com/news | News | https://www.firstround.com/news/feed |

### Tier 2 - Top Tier Funds (Priority 2)

| Firm | Source Name | Content URL | Type |
|------|-------------|-------------|------|
| Benchmark | `benchmark` | https://www.benchmark.com | Blog (minimal) |
| Greylock | `greylock` | https://greylock.com/blog/ | Blog | https://greylock.com/feed/ |
| Lightspeed | `lightspeed` | https://lsvp.com/stories/ | Blog | https://lsvp.com/feed/ |
| Index Ventures | `index` | https://www.indexventures.com/perspectives/ | Blog | https://www.indexventures.com/feed/ |
| Union Square Ventures | `usv` | https://www.usv.com/writing/ | Blog | https://www.usv.com/feed/ |
| Founders Fund | `foundersfund` | https://foundersfund.com/anatomy-of-next/articles-essays-more/ | Blog | https://foundersfund.com/feed/ |
| Khosla Ventures | `khosla` | https://www.khoslaventures.com/venture-assistance-blog/ | Blog | https://www.khoslaventures.com/feed/ |
| NEA | `nea` | https://www.nea.com/blog | Blog | https://www.nea.com/feed/ |

### Tier 3 - Notable Specialized (Priority 3)

| Firm | Source Name | Content URL | Type |
|------|-------------|-------------|------|
| Accel | `accel` | https://www.accel.com/insights | Blog |
| GGV / Notable Capital | `notable` | https://www.notablecap.com/insights | Blog |
| General Catalyst | `generalcatalyst` | https://www.generalcatalyst.com/perspectives | Blog |
| Thrive Capital | `thrive` | https://www.thrivecap.com/insights | Blog |
| Coatue | `coatue` | https://www.coatue.com/insights | Blog |
| Tiger Global | `tigerglobal` | https://www.tigerglobal.com/insights | Blog |

## Gains / Value Proposition

1. **Deal Flow Intelligence** - Track new investments, portfolio company milestones, IPOs
2. **Thesis Tracking** - Follow partner perspectives on market trends (AI, crypto, bio, climate, etc.)
3. **Talent Signals** - Partner hires, new GPs, firm expansions indicate strategic shifts
4. **Founder Intelligence** - Learn from portfolio company case studies and playbooks
5. **LP/GPS Intelligence** - Fund raises, new fund announcements, LP updates
6. **Market Narrative Control** - VCs shape industry narratives; tracking them reveals emerging trends early
7. **Competitive Intelligence** - See which firms are leading in which sectors

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        feedy Pipeline                            │
├─────────────────────────────────────────────────────────────────┤
│  Sources (VC Firms)          │  Storage          │  Output      │
│  ─────────────────────────   │  ──────────────   │  ──────────  │
│  • sequoia                   │  • SQLite         │  • CLI list  │
│  • sequoia-inference         │  • Dedupe by URL  │  • AI Digest │
│  • a16z                      │  • Source tagging │  • Slack     │
│  • a16z-substack             │  • Date filtering │  • Email     │
│  • ycombinator               │  • Stats per src  │  • Web API   │
│  • firstround                │                   │              │
│  • firstround-news           │                   │              │
│  • greylock                  │                   │              │
│  • lightspeed                │                   │              │
│  • index                     │                   │              │
│  • usv                       │                   │              │
│  • foundersfund              │                   │              │
│  • khosla                    │                   │              │
│  • nea                       │                   │              │
└─────────────────────────────────────────────────────────────────┘
```

## Implementation Tasks

### Phase 1: Core Infrastructure (Week 1)

#### Task 1.1: Create VC Source Base Class (Optional)
- Consider if we need a `VCFeedSource` base class with common VC-specific logic
- For now, stick to existing `BaseFeedSource` pattern

#### Task 1.2: Add Source Registry Entries
- Update `feedy/cli.py` `_build_sources()` registry
- Add all VC source names

#### Task 1.3: Update Default Config
- Add VC sources to `DEFAULT_SOURCES` in `feedy/config.py`
- Consider making them opt-in (not in default) since user specifically wants VC focus

### Phase 2: Source Implementations (Week 1-2) - PARALLEL WORKSTREAMS

Each source is independent - perfect for worktree parallelization.

#### Worktree 1: Sequoia Sources
- `feedy/sources/sequoia.py` - Main blog (sequoiacap.com/stories)
- `feedy/sources/sequoia_inference.py` - Substack (inferencebysequoia.substack.com)

#### Worktree 2: a16z Sources
- `feedy/sources/a16z.py` - Main site (a16z.com/news-content/)
- `feedy/sources/a16z_substack.py` - Substack (a16z.news)

#### Worktree 3: Y Combinator
- `feedy/sources/ycombinator.py` - Blog (ycombinator.com/blog)

#### Worktree 4: First Round Capital
- `feedy/sources/firstround.py` - Review (review.firstround.com)
- `feedy/sources/firstround_news.py` - News (firstround.com/news)

#### Worktree 5: Tier 2 Firms (Batch)
- `feedy/sources/greylock.py`
- `feedy/sources/lightspeed.py`
- `feedy/sources/index.py`
- `feedy/sources/usv.py`
- `feedy/sources/foundersfund.py`
- `feedy/sources/khosla.py`
- `feedy/sources/nea.py`

### Phase 3: Testing & Polish (Week 2)

#### Task 3.1: Unit Tests
- Create test file per source in `tests/sources/`
- Mock HTTP responses
- Test parse/transform logic

#### Task 3.2: Integration Test
- Run `feedy fetch` with all VC sources
- Verify deduplication works
- Verify AI summarization works for VC content

#### Task 3.3: Config & CLI Polish
- Add `--vc-only` flag to fetch only VC sources
- Add VC category filtering in digest
- Update `feedy sources` command to show VC sources

#### Task 3.4: Documentation
- Update README with VC sources
- Update CONTRIBUTING.md with VC source patterns
- Add config example for VC-only setup

## Technical Details

### Source Implementation Pattern

```python
# feedy/sources/sequoia.py
from feedy.sources.base import BaseFeedSource, FeedEntry
import httpx
from bs4 import BeautifulSoup

class SequoiaSource(BaseFeedSource):
    @property
    def name(self) -> str:
        return "sequoia"

    def fetch(self) -> list:
        # Fetch HTML from sequoiacap.com/stories
        ...

    def parse(self, raw: list) -> list[dict]:
        # Extract title, url, date from HTML
        ...

    def to_dict(self, entry: dict) -> FeedEntry:
        return FeedEntry(
            url=entry["url"],
            title=entry["title"],
            date=entry.get("date", ""),
            source=self.name,
            summary="",
        )
```

### Substack Sources

Substack provides RSS feeds at `/feed`:
- `https://inferencebysequoia.substack.com/feed`
- `https://www.a16z.news/feed`

Use feedparser or parse XML directly.

### RSS Feed Sources

Most VC blogs have RSS at `/feed` or `/rss`:
- Check each site for feed autodiscovery
- Use `feedparser` library if needed (add to deps)

## Worktree Setup

```bash
# Main branch stays clean
git worktree add ../feedy-vc-sequoia main
git worktree add ../feedy-vc-a16z main
git worktree add ../feedy-vc-yc main
git worktree add ../feedy-vc-firstround main
git worktree add ../feedy-vc-tier2 main
```

Each worktree gets a focused task:
- Worktree 1: Sequoia (2 sources)
- Worktree 2: a16z (2 sources)
- Worktree 3: Y Combinator (1 source)
- Worktree 4: First Round (2 sources)
- Worktree 5: Tier 2 batch (7 sources)

## Subagent Delegation Plan

Each worktree gets a subagent with:
1. Clear source specification (URLs, selectors, date formats)
2. Template source implementation
3. Test expectations
4. Integration verification steps

## Success Criteria

- [ ] All 15+ VC sources fetch without errors
- [ ] Deduplication works across sources (same story on multiple VC blogs)
- [ ] AI summaries are relevant for VC content (investment announcements, theses, etc.)
- [ ] Daily fetch completes in < 60 seconds
- [ ] `feedy digest --source sequoia` works
- [ ] `feedy fetch --vc-only` works (new flag)
- [ ] GitHub Actions updated for daily VC fetch

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Site structure changes | Robust selectors, fallback parsing |
| Rate limiting | Respect robots.txt, add delays, cache |
| No RSS feeds | HTML scraping with BeautifulSoup (current pattern) |
| Paywalled content | Skip gracefully, log warning |
| Substack changes | Use official RSS feeds |
| Duplicate content | URL-based dedupe + title similarity check |

## Future Enhancements

1. **Partner-level tracking** - Filter by specific partners
2. **Sector tagging** - AI/ML, Bio, Crypto, Climate, FinTech, etc.
3. **Portfolio company tracking** - Cross-reference with Crunchbase/API
4. **Fund announcement alerts** - New fund raises, closings
5. **Podcast transcripts** - Many VCs have podcasts (Training Data, a16z Podcast, etc.)
6. **Twitter/X integration** - Partner tweets often break news first
7. **LP update parsing** - When available (quarterly letters)

## Dependencies

Current deps sufficient. May need:
- `feedparser` for RSS feeds (optional - can parse XML with stdlib)
- `lxml` for faster XML parsing (optional)

## Timeline

- **Day 1-2**: Setup worktrees, create Phase 1 tasks
- **Day 2-5**: Parallel source implementation (5 worktrees)
- **Day 5-6**: Integration, testing, config updates
- **Day 7**: Documentation, GitHub Actions, merge

Total: ~1 week with parallel workstreams