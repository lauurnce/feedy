# Security Policy

## Supported versions

Only the latest commit on `main` is supported.

## Reporting a vulnerability

Report privately to the repository owner rather than opening a public issue.

## Threat model

feedy assumes a single trusted operator on a local machine. The JSON API ships
without authentication and must not be exposed publicly without a proxy in front.

## Credentials

All secrets are read from the environment. Never commit a token; `.env.example`
lists every variable the tool reads.
