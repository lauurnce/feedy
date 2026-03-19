# Available Sources

- Each source is an adapter for one upstream service and is enabled independently.
- Hacker News — public items, no credentials required, which makes it the best first test.
- Anthropic — tracks posts published by Anthropic.
- OpenAI — tracks posts published by OpenAI.
- Meta — tracks posts published by Meta.
- X — tracks posts from configured accounts; requires credentials.
- Telegram — tracks configured channels; requires credentials.
- TikTok — tracks configured accounts; requires credentials.
- A source must be both registered and enabled in config before a fetch will use it.
- Credentials come from the environment, named per source so several can coexist.
