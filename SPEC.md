# Worktree: vc-firstround
## Task: Implement First Round Capital Sources

### Sources to Implement

1. **firstround** - First Round Review at https://review.firstround.com
2. **firstround-news** - First Round News at https://www.firstround.com/news

### Source 1: firstround (review.firstround.com)

**URL**: https://review.firstround.com
**Content**: Deep-dive tactical articles, founder interviews, frameworks, playbooks
**Quality**: "Peerless for delivering helpful frameworks and advice for founders"
**RSS**: Likely at `/feed` or `/rss` (FeedBurner historically used)

**HTML Structure** (from research):
- Article listings with title, excerpt, author, date
- Categories: Hiring, Product, Fundraising, Leadership, etc.
- Author profiles with multiple articles

**Selectors to investigate**:
- Article containers: `.post`, `article`, `.article-card`
- Title: `h1`, `h2`, `.post-title a`
- Link: `a` tag on title
- Date: `.date`, `time[datetime]`, `.post-date`
- Author: `.author`, `.byline`
- Categories: `.category`, `.tag`

**RSS Feed**: Check for FeedBurner or native RSS at `/feed`

### Source 2: firstround-news (firstround.com/news)

**URL**: https://www.firstround.com/news
**Content**: Firm announcements, new fund launches, partner hires, portfolio news, Applied Intelligence publication
**RSS**: Likely at `/news/feed`

**HTML Structure**:
- News listings with title, date, excerpt
- Categories: News, Announcements

**Selectors to investigate**:
- Similar to review site
- News-specific containers

### Additional First Round Properties (Future)
- **redeye** - Josh Kopelman's blog: https://redeye.firstround.com (RSS at feeds.feedburner.com/redeyevc)
- **waytooearly** - Early stage blog: https://waytooearly.firstround.com (RSS at feeds.feedburner.com/waytooearly)

### Files to Create

```
/Users/lauurnce/projects/feedy-vc-firstround/feedy/sources/firstround.py
/Users/lauurnce/projects/feedy-vc-firstround/feedy/sources/firstround_news.py
/Users/lauurnce/projects/feedy-vc-firstround/tests/sources/test_firstround.py
/Users/lauurnce/projects/feedy-vc-firstround/tests/sources/test_firstround_news.py
```

### Testing Requirements

- Mock HTTP responses for both sources
- Test parse() with sample HTML/RSS
- Test to_dict() produces valid FeedEntry
- Test date parsing
- Test deduplication
- Test RSS feed parsing (if FeedBurner, handle redirects)

### Integration

After implementation, the main repo will need:
1. Import in `feedy/cli.py` registry
2. Add to `DEFAULT_SOURCES` in `feedy/config.py`

### Success Criteria

- [ ] Both sources fetch without errors
- [ ] Entries have valid URLs, titles, dates
- [ ] No duplicate entries within a fetch
- [ ] Dates parse correctly to YYYY-MM-DD
- [ ] Source names match registry keys ("firstround", "firstround-news")
- [ ] RSS feeds work (handle FeedBurner redirects)