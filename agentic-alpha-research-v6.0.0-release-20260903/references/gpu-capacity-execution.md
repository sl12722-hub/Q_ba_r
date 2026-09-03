# GPU Capacity Execution

Use the project GPU capacity runner for immutable out-of-fold predictions when
several execution policies or capital tiers must be replayed. It keeps policy,
capital and instrument state in float64 tensors while reading Parquet with one
CPU thread. It must preserve the CPU engine's stable factor/instrument tie-break,
fold resets, buffered tails, participation clipping, one-way traded-notional
costs and position marking.

Before first use on a new execution-contract version, run one identical policy
and all required capital tiers through both engines. Require identical policy
keys and trading-day counts. Compare return, Sharpe, fill rate, mean gross
exposure, requested notional and executed notional with tight float64
tolerances. Reject the GPU result if the mismatch is material; do not average or
choose between engines by factor quality.

After parity passes, run interacting entry tails, exit buffers, rebalance
schedules, participation rates and cost assumptions in one native Cartesian
batch. Audit its `capacity_frontier.csv` with
`scripts/audit_capacity_cartesian.py --frontier-csv`. Missing policies, missing
capital tiers or conflicting duplicate metrics fail closed. Grid completeness
does not imply quality: promotion still requires one unchanged policy to clear
all capital tiers.

Record wall seconds, process CPU seconds, CPU-to-wall ratio, peak CUDA bytes,
device name, dense panel shape and source hashes. Prefer chunked GPU policy
batches if memory pressure appears. Use a one-thread CPU replay only as the
bounded parity control or when CUDA is unavailable.
