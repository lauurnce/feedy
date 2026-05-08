# Testing Notes

- Tests are written before the code they cover, and each starts by failing for the right reason.
- No test hits the network. Transports are stubbed so the suite runs offline and fast.
- Each module has a matching test file, which makes missing coverage obvious at a glance.
