# Notifier Notes

- A notifier delivers an already-rendered digest. It never selects or formats content itself.
- Delivery failure never discards the digest; storage already holds everything needed to retry.
- With several channels configured, one failing channel must not block the others.
- Channels are chosen from config so enabling one requires no code change.
