# Workflow Notes

- One logical change per commit, so history reads as a sequence of decisions.
- Failing tests land in their own commit before the implementation that satisfies them.
- Messages use a type prefix and describe the change, not the file that changed.
- Small commits are easier to review, revert and bisect when something breaks later.
- The scope in a prefix names the module touched, which makes log filtering useful.
- Multi-step work gets a short plan document before code, kept alongside the repo.
- Refactors ship separately from behaviour changes so a revert stays surgical.
- Before pushing: tests pass, the tree is clean and the branch is current with origin.
- Linear history keeps the log readable and makes bisecting straightforward.
- Documentation changes use a docs prefix so they filter cleanly out of a code review.
