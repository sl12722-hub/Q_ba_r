# Active Data Protocol

## Split

| Purpose | Dates | Search feedback |
| --- | --- | --- |
| Development and training | 2019-2022 plus 2024 | Allowed |
| Isolated regime holdout | 2023 | Forbidden |
| External daily context | 2025-2026 hsjday | Forbidden by default |

This split is intentionally non-chronological. Because development includes
2024, the 2023 result is a regime-transfer test, not forward out-of-time or
simulated-live evidence. Always preserve this statement in reports.

## Compatibility

Candidates, diversity archives, model selection, hyperparameters, learned
directions and trajectories created under the former 2019-2023 development
protocol are incompatible. They may be inspected as historical evidence but
must not initialize, rank or train a run under the active protocol.

Give every run a protocol identifier derived from the normalized split,
decision time, label definition, universe contract and cost policy. Reject
state whose protocol identifier differs.

## Calendar Gap

The development panel omits all of 2023. Never define the next session after a
late-2022 row as an early-2024 row. The project's target builder rejects links
across calendar gaps longer than 14 days; preserve and test this invariant.

## Point-in-Time Inputs

Promotion requires point-in-time CSI1000 membership plus exact pre-open
security status, including suspension and limit prices. An unfiltered panel may
be used only for diagnostic control-flow tests and must be labeled
`diagnostic_only`.

## hsjday Boundary

The local TDX-compatible daily files extend through 2026-07-13. They are not
confirmed adjusted prices, include non-equity instruments and may overlap a
competition hidden period. Do not use 2025-2026 returns, ranks or fitted weights
to select a submission or development champion. Use the data only for isolated
research expressly permitted by the current task and protocol.
