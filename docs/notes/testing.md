# Testing Notes

- Tests are written before the code they cover, and each starts by failing for the right reason.
- No test hits the network. Transports are stubbed so the suite runs offline and fast.
- Each module has a matching test file, which makes missing coverage obvious at a glance.
- Every test gets a fresh temporary database, so no test can observe another's writes.
- Tests must pass in any order. Order dependence signals leaked state, not a flaky test.
- A failing assertion should say what was expected and what happened, without needing a debugger.
- Test behaviour through the public interface; private helpers change too often to pin down.
- A new source ships with tests for the happy path, an empty response and a malformed payload.
- Digest rendering is deterministic, which makes snapshot comparison a good fit.
- Test names describe the behaviour asserted, so a failure reads as a sentence.
- Error paths deserve tests too; assert on the failure, not just the success case.
- A fast suite gets run often. Anything slow belongs behind an explicit marker.
- Stub at the boundary, not inside the module under test, or the test asserts on itself.
- Prefer small explicit setup in the test over a fixture that hides what is being tested.
- Every escaped bug gets a regression test before the fix lands, not after.
