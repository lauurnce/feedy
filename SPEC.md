# Worktree: vc-a16z
## Task: Implement Andreessen Horowitz (a16z) Sources

### Sources to Implement

1. **a16z** - Main site at https://a16z.com/news-content/
2. **a16z-substack** - Substack at https://www.a16z.news

### Source 1: a16z (a16z.com/news-content/)

**URL**: https://a16z.com/news-content/
**Content**: Expert news, podcasts, newsletters, articles from a16z partners
**Categories**: Multiple newsletter sections (AI Policy, Crypto, Fintech, Bio, Enterprise, etc.)

**HTML Structure** (from research):
- News content page with article cards
- Each card: title, excerpt, link, category tags
- Multiple newsletter sections on page

**Selectors to investigate**:
- Article containers: `.post-card`, `.article-card`, `article`
- Title: `h2`, `h3`, `.post-title`
- Link: `a` tag
- Date: `.date`, `time[datetime]`
- Category: `.category`, `.tag`

**RSS Feed**: Check for `/feed` or `/news-content/feed`

**Newsletters** (each may have own feed):
- a16z News (daily)
- a16z AI Policy Brief
- Web3 Weekly (crypto)
- Speedrun (gaming/consumer)
- Fintech Newsletter
- Bio Newsletter
- Enterprise Newsletter
- Cultural Leadership Fund

### Source 2: a16z-substack (a16z.news)

**URL**: https://www.a16z.news
**Content**: "It's time to build" - founder/operator content, daily newsletter
**Feed**: RSS at https://www.a16z.news/feed
**Subscribers**: 260,000+

**RSS Structure** (standard Substack):
- `<item>` with `<title>`, `<link>`, `<pubDate>`, `<description>`
- Daily newsletter format

### Files to Create

```
/Users/lauurnce/projects/feedy-vc-a16z/feedy/sources/a16z.py
/Users/lauurnce/projects/feedy-vc-a16z/feedy/sources/a16z_substack.py
/Users/lauurnce/projects/feedy-vc-a16z/tests/sources/test_a16z.py
/Users/lauurnce/projects/feedy-vc-a16z/tests/sources/test_a16z_substack.py
```

### Testing Requirements

- Mock HTTP responses for both sources
- Test parse() with sample HTML/RSS
- Test to_dict() produces valid FeedEntry
- Test date parsing for RFC 822 (Substack) and site formats
- Test deduplication within single fetch
- Test handling of multiple newsletter sections

### Integration

After implementation, the main repo will need:
1. Import in `feedy/cli.py` registry
2. Add to `DEFAULT_SOURCES` in `feedy/config.py` (or keep opt-in)

### Success Criteria

- [ ] Both sources fetch without errors
- [ ] Entries have valid URLs, titles, dates
- [ ] No duplicate entries within a fetch
- [ ] Dates parse correctly to YYYY-MM-DD
- [ ] Source name matches registry key ("a16z", "a16z-substack")