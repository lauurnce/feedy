# Notifier Notes

- A notifier delivers an already-rendered digest. It never selects or formats content itself.
- Delivery failure never discards the digest; storage already holds everything needed to retry.
- With several channels configured, one failing channel must not block the others.
- Channels are chosen from config so enabling one requires no code change.
- No configured channel is a valid setup; the run completes and simply delivers nothing.
- Channels differ in size limits. Split or trim at the notifier, not upstream in the digest.
- Tokens come from config or environment, and are never logged, even at debug level.
- Retry once on a transient network error, then report the failure and move on.
- Each channel picks the format it renders best; plain text is the safe default.
- Delivery runs last so a channel outage cannot cost a fetch or a summarisation.
- Notifier tests assert on the payload handed to the transport, never on live delivery.
- Failure messages name the channel, so a multi-channel run points at the right one.
