# Web API Notes

- The web layer exposes stored entries read-only. It never triggers fetches on its own.
- API filters mirror CLI options, so the two interfaces stay conceptually identical.
- Endpoints returning collections take a limit, so no response is unbounded by accident.
- JSON is the single response format; rendering belongs to whatever consumes the API.
- Errors return a proper status code and a short message, never a stack trace.
