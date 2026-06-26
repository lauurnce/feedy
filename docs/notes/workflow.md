# Workflow Notes

- One logical change per commit, so history reads as a sequence of decisions.
- Failing tests land in their own commit before the implementation that satisfies them.
- Messages use a type prefix and describe the change, not the file that changed.
- Small commits are easier to review, revert and bisect when something breaks later.
