# Worktree: vc-sequoia
## Task: Implement Sequoia Capital Sources

### Sources to Implement

1. **sequoia** - Main blog at https://sequoiacap.com/stories
2. **sequoia-inference** - Substack at https://inferencebysequoia.substack.com

### Source 1: sequoia (sequoiacap.com/stories)

**URL**: https://sequoiacap.com/stories
**Content**: Long-form founder profiles, market/technology perspectives, portfolio company news
**Categories**: News, Perspective, Spotlight

**HTML Structure** (from research):
- Stories listed on page with article links
- Each story has: title, URL, date, category badge
- Pagination or infinite scroll likely

**Selectors to investigate**:
- Article containers: likely `.story-card`, `article`, or similar
- Title: `h2`, `h3`, or `.story-title`
- Link: `a` tag wrapping title
- Date: `.date`, `time`, or meta tag
- Category: `.category`, `.badge`

**Date Format**: Likely "Aug 26, 2026" or ISO in datetime attribute

**Implementation Notes**:
- Check for RSS feed at `/feed` or `/stories/feed`
- If no RSS, scrape HTML with BeautifulSoup
- Handle pagination (likely `?page=2` or similar)
- Filter by category if needed (News, Perspective, Spotlight)

### Source 2: sequoia-inference (inferencebysequoia.substack.com)

**URL**: https://inferencebysequoia.substack.com
**Content**: AI-generated insights from Sequoia podcasts, events, written perspectives
**Feed**: RSS at https://inferencebysequoia.substack.com/feed

**RSS Structure** (standard Substack):
- `<item>` with `<title>`, `<link>`, `<pubDate>`, `<description>`
- `<description>` contains full HTML content
- `<pubDate>` in RFC 822 format

**Implementation**: Use feedparser or parse XML directly

### Files to Create

```
/Users/lauurnce/projects/feedy-vc-sequoia/feedy/sources/sequoia.py
/Users/lauurnce/projects/feedy-vc-sequoia/feedy/sources/sequoia_inference.py
/Users/lauurnce/projects/feedy-vc-sequoia/tests/sources/test_sequoia.py
/Users/lauurnce/projects/feedy-vc-sequoia/tests/sources/test_sequoia_inference.py
```

### Testing Requirements

- Mock HTTP responses for both sources
- Test parse() with sample HTML/RSS
- Test to_dict() produces valid FeedEntry
- Test date parsing for various formats
- Test deduplication within single fetch

### Integration

After implementation, the main repo will need:
1. Import in `feedy/cli.py` registry
2. Add to `DEFAULT_SOURCES` in `feedy/config.py` (or keep opt-in)
3. Run `feedy fetch` to verify

### Success Criteria

- [ ] Both sources fetch without errors
- [ ] Entries have valid URLs, titles, dates
- [ ] No duplicate entries within a fetch
- [ ] Dates parse correctly to YYYY-MM-DD
- [ ] Source name matches registry key ("sequoia", "sequoia-inference")