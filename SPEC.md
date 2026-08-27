# Worktree: vc-tier2
## Task: Implement Tier 2 VC Firm Sources (Batch)

### Sources to Implement (7 sources)

1. **greylock** - https://greylock.com/blog/
2. **lightspeed** - https://lsvp.com/stories/
3. **index** - https://www.indexventures.com/perspectives/
4. **usv** - https://www.usv.com/writing/
5. **foundersfund** - https://foundersfund.com/anatomy-of-next/articles-essays-more/
6. **khosla** - https://www.khoslaventures.com/venture-assistance-blog/
7. **nea** - https://www.nea.com/blog

---

### Source 1: greylock (greylock.com/blog/)

**URL**: https://greylock.com/blog/
**Content**: News & Insights, Portfolio News, Greymatter podcast, Firm News, Change Agents
**Sub-sections**:
- /blog/ (main)
- /blog/portfolio-news/
- /blog/greymatter/ (podcast)
- /blog/firm-news/
- /change-agents/

**RSS**: Check for `/feed` or `/blog/feed`

**HTML Structure**:
- Article grid with title, excerpt, date, category
- Category tags on each post

---

### Source 2: lightspeed (lsvp.com/stories/)

**URL**: https://lsvp.com/stories/
**Content**: Founder stories, partner perspectives, industry insights, investment announcements
**RSS**: Check for `/feed` or `/stories/feed`
**Newsletter**: https://newsletter.lsvp.com/ (Substack - separate source if needed)

**HTML Structure**:
- Story cards with title, excerpt, date, author
- Categories/tags

---

### Source 3: index (indexventures.com/perspectives/)

**URL**: https://www.indexventures.com/perspectives/
**Content**: Perspectives pieces, news, insights, open source content
**Sub-sections**:
- /perspectives/ (main)
- /perspectives/news/
- /perspectives/insights/
- /opensource/

**RSS**: Check for `/feed` or `/perspectives/feed`

---

### Source 4: usv (usv.com/writing/)

**URL**: https://www.usv.com/writing/
**Content**: Partner blog posts (Fred Wilson, Albert Wenger, Nick Grossman, etc.)
**Also**: https://blog.usv.com/ (Paragraph/Substack mirror with RSS)
**RSS**: https://blog.usv.com/ has RSS at https://paragraph.com/api/blogs/rss/@usv

**HTML Structure**:
- Post listings with title, author, date, excerpt
- Author-specific views

---

### Source 5: foundersfund (foundersfund.com/anatomy-of-next/)

**URL**: https://foundersfund.com/anatomy-of-next/articles-essays-more/
**Content**: Anatomy of Next podcast essays, articles, Hereticon content
**Style**: Long-form, contrarian, "thoughtcrime" content

**HTML Structure**:
- Article listings with title, date, author
- Podcast episode pages

---

### Source 6: khosla (khoslaventures.com/venture-assistance-blog/)

**URL**: https://www.khoslaventures.com/venture-assistance-blog/
**Content**: Vinod Khosla's writings, venture assistance philosophy, AI/climate/health insights
**Also**: /entrepreneurs/ section for entrepreneurial resources

**HTML Structure**:
- Blog post listings
- Video/content embeds

---

### Source 7: nea (nea.com/blog)

**URL**: https://www.nea.com/blog
**Content**: "The Current" series, AI Stack series, consumer tech insights, portfolio news
**Sub-sections**: /the-current/, /blog/

**HTML Structure**:
- Article cards with title, category, date
- Series-based organization

---

### Files to Create (per source)

```
/Users/lauurnce/projects/feedy-vc-tier2/feedy/sources/greylock.py
/Users/lauurnce/projects/feedy-vc-tier2/feedy/sources/lightspeed.py
/Users/lauurnce/projects/feedy-vc-tier2/feedy/sources/index.py
/Users/lauurnce/projects/feedy-vc-tier2/feedy/sources/usv.py
/Users/lauurnce/projects/feedy-vc-tier2/feedy/sources/foundersfund.py
/Users/lauurnce/projects/feedy-vc-tier2/feedy/sources/khosla.py
/Users/lauurnce/projects/feedy-vc-tier2/feedy/sources/nea.py

/Users/lauurnce/projects/feedy-vc-tier2/tests/sources/test_greylock.py
/Users/lauurnce/projects/feedy-vc-tier2/tests/sources/test_lightspeed.py
/Users/lauurnce/projects/feedy-vc-tier2/tests/sources/test_index.py
/Users/lauurnce/projects/feedy-vc-tier2/tests/sources/test_usv.py
/Users/lauurnce/projects/feedy-vc-tier2/tests/sources/test_foundersfund.py
/Users/lauurnce/projects/feedy-vc-tier2/tests/sources/test_khosla.py
/Users/lauurnce/projects/feedy-vc-tier2/tests/sources/test_nea.py
```

### Testing Requirements (per source)

- Mock HTTP responses
- Test parse() with sample HTML
- Test to_dict() produces valid FeedEntry
- Test date parsing for each site's format
- Test deduplication
- Test RSS feed if available

### Implementation Priority Order

1. **greylock** - Clear blog structure, multiple sub-sections
2. **lightspeed** - Active blog, clear story format
3. **usv** - RSS available via Paragraph, partner posts high value
4. **index** - Perspectives format, multiple categories
5. **nea** - The Current series, regular cadence
6. **khosla** - Vinod's writing, unique perspective
7. **foundersfund** - Anatomy of Next, less frequent but high signal

### Integration

After implementation, the main repo will need:
1. Import all 7 in `feedy/cli.py` registry
2. Add to `DEFAULT_SOURCES` in `feedy/config.py`

### Success Criteria (per source)

- [ ] Source fetches without errors
- [ ] Entries have valid URLs, titles, dates
- [ ] No duplicate entries within a fetch
- [ ] Dates parse correctly to YYYY-MM-DD
- [ ] Source name matches registry key