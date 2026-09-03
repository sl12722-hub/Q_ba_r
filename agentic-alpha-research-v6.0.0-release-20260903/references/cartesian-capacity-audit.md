# Cartesian Capacity Audit

The legacy capacity frontier mode changes one policy axis around a baseline.
Its row count is not evidence that interactions among several execution axes
were run. The project runner also exposes an explicit `--cartesian` mode; use
it whenever two or more policy axes are being selected jointly.

When an experiment claims a complete combination of entry tails, exit buffers
and rebalance schedules, either run every fixed policy in its own directory or
write one native Cartesian `capacity_frontier.csv`. Then use
`scripts/audit_capacity_cartesian.py` with `--grid-root` for legacy directories
or `--frontier-csv` for the native table. The audit must find every valid policy
combination, every capital tier and identical duplicate metrics before a grid
can be called complete.

For large native grids produced from fixed OOF predictions, follow
[gpu-capacity-execution.md](gpu-capacity-execution.md). GPU acceleration changes
the executor, not the execution contract or the completeness gate.

Report the worst capital-tier Sharpe, return and fill rate for each intact
policy. A policy passes only when the same fixed combination clears every
capital tier. Never combine the best exit buffer from one run with the best
rebalance schedule from another run.
