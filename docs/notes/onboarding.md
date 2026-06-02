# Onboarding Notes

- feedy pulls items from several feeds into one local store and renders periodic digests.
- Start with `sources` to confirm the install works before touching config or credentials.
- Read the CLI first; it names every capability and points at the module behind each one.
- The full suite runs offline in seconds, so run it before and after any change.
- Dependencies come from the lockfile, which keeps every machine on the same versions.
- A first run needs no config at all; defaults are enough to fetch a public source.
- Copy the simplest existing source, change the fetch and normalise steps, register the name.
