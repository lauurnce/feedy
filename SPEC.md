# Worktree: vc-yc
## Task: Implement Y Combinator Source

### Sources to Implement

1. **ycombinator** - Blog at https://www.ycombinator.com/blog

### Source: ycombinator (ycombinator.com/blog)

**URL**: https://www.ycombinator.com/blog
**Content**: YC announcements, Demo Day updates, partner posts, portfolio company milestones, startup advice
**Tags/Categories**: YC News, Startup Jobs, Startup School

**HTML Structure** (from research):
- Blog index with post cards
- Each post: title, excerpt, date, author, tags
- Pagination at bottom
- Tag filter URLs: `/blog/tag/yc-news`

**Selectors to investigate**:
- Post containers: `.post-card`, `article`, `.blog-post`
- Title: `h2`, `h3`, `.post-title a`
- Link: `a` tag on title
- Date: `.date`, `time[datetime]`, `.post-date`
- Author: `.author`, `.post-author`
- Tags: `.tag`, `.post-tag`

**RSS Feed**: Check for `/blog/feed` or `/feed`

**Date Format**: "Dec 18, 2025" or similar

**Special Content**:
- Demo Day announcements
- New partner/GP announcements
- Portfolio company IPOs/milestones
- YC program updates (batch dates, application deadlines)
- Startup School content

### Files to Create

```
/Users/lauurnce/projects/feedy-vc-yc/feedy/sources/ycombinator.py
/Users/lauurnce/projects/feedy-vc-yc/tests/sources/test_ycombinator.py
```

### Testing Requirements

- Mock HTTP responses
- Test parse() with sample HTML
- Test to_dict() produces valid FeedEntry
- Test date parsing for "Month DD, YYYY" format
- Test pagination handling (if implemented)
- Test tag/category extraction (optional - for future filtering)

### Integration

After implementation, the main repo will need:
1. Import in `feedy/cli.py` registry
2. Add to `DEFAULT_SOURCES` in `feedy/config.py`

### Success Criteria

- [ ] Source fetches without errors
- [ ] Entries have valid URLs, titles, dates
- [ ] No duplicate entries within a fetch
- [ ] Dates parse correctly to YYYY-MM-DD
- [ ] Source name matches registry key ("ycombinator")
- [ ] Handles pagination (at least first page)