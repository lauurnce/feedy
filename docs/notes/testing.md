# Testing Notes

- Tests are written before the code they cover, and each starts by failing for the right reason.
- No test hits the network. Transports are stubbed so the suite runs offline and fast.
- Each module has a matching test file, which makes missing coverage obvious at a glance.
- Every test gets a fresh temporary database, so no test can observe another's writes.
- Tests must pass in any order. Order dependence signals leaked state, not a flaky test.
- A failing assertion should say what was expected and what happened, without needing a debugger.
