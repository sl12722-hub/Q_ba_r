# Changelog

## V6.0.0 - 2026-09-03

Major causal-representation and research-anchor release.

- Added a fold-evidence router from shared static-level model failure to causal
  cross-sectional rank innovation instead of further weight tuning.
- Required pure innovation as a diagnostic control before combining levels and
  innovations, then required an ordered lag neighborhood.
- Produced three complete-contract hybrid XGBoost quality survivors at lags 3,
  5 and 10; all three repaired the former common worst fold and all three passed
  the local quality gate.
- Required capacity work to include the exact daily research-policy anchor in
  addition to the slower execution stress grid.
- Rejected the strongest lag-10 survivor at capacity despite Sharpe near 3.20
  and return above 626%, because all capital tiers had fill near 0.8925 below
  the unchanged 0.90 gate.

## V5.9.0 - 2026-09-03

Minor model-fold-concordance release.

- Added deterministic fold-vector comparison across learned-model ensemble
  members and their fixed ensemble.
- Distinguished variance diversification from shared structural fold failure.
- Closed post-hoc weight tuning when three XGBoost memory scales had mean
  pairwise fold-IC correlation 0.892, jointly failed fold 12 and their equal
  ensemble worsened that fold from -0.0104 to -0.0162.
- Added fail-closed tests for mismatched folds and deterministic replay.

## V5.8.0 - 2026-09-03

Minor complete-experiment-contract release.

- Required explicit evaluation, walk-forward, portfolio and model contracts
  before learned trials can be compared or ensembled.
- Added a deterministic fail-closed contract auditor with controlled model-axis
  exceptions for predeclared neighborhoods such as training lookback.
- Used three attractive but protocol-mismatched XGBoost runs as real negative
  evidence: omitted purge, embargo, feature and portfolio fields changed fold
  dates, fold counts and OOF keys while still producing passing headline metrics.
- Added regression tests for incomplete contracts, purge mismatch, permitted
  model-axis variation and deterministic report hashing.

## V5.7.0 - 2026-09-03

Minor model-specification neighborhood release.

- Added deterministic structural-contract and ordered-neighborhood auditing for
  label horizons, smoothing spans and related model specifications.
- Required at least one adjacent pair to pass the complete quality gate before
  an ordered specification can proceed.
- Marked the regime-conditioned DeepCross 1/3/5-day neighborhood exhausted:
  zero of three points passed despite the isolated 5-day point reaching net
  Sharpe 0.858 with regime context and 1.393 without it.
- Added fail-closed handling for incomplete and structurally mixed report sets.

## V5.6.0 - 2026-09-03

Minor learned-model failure-decomposition release.

- Replaced the catch-all post-gate cost diagnosis with explicit concurrent
  rank-tail mismatch, tail instability, regime concentration, execution cost
  and weak-rank failure modes.
- Made execution-cost classification depend on net Sharpe, return or turnover
  thresholds rather than any unrelated quality-gate rejection.
- Used T164 as a real counterexample: net Sharpe 1.393 and return 0.945 no longer
  hide weak IC and worst-fold IC -0.0347 behind a false cost diagnosis.
- Kept capacity fail-closed unless the complete development quality gate passes.

## V5.5.0 - 2026-09-03

Major GPU capacity-execution release.

- Added a float64 GPU-batched Cartesian capacity path for immutable OOF
  predictions while bounding Parquet and diagnostic CPU work to one thread.
- Required a real one-policy CPU parity control before GPU results can influence
  selection, covering return, Sharpe, fill, exposure and traded notionals.
- Extended Cartesian auditing to native multi-policy frontier tables and made
  missing combinations or capital tiers fail closed.
- Replayed a 945-day by 2,250-instrument OOF panel: the GPU engine matched the
  CPU engine to floating-point tolerance and reduced one-policy wall time from
  14.25 seconds to 2.08 seconds.
- Evaluated and audited 12 policies across three capital tiers in 4.00 seconds;
  all 36 rows were complete and no weak policy was promoted.

## V5.4.0 - 2026-09-02

Minor Cartesian-capacity completeness release.

- Distinguished one-axis capacity frontiers from complete interacting-policy
  grids.
- Added deterministic fixed-policy and capital-tier coverage auditing with
  duplicate-conflict detection and source CSV hashes.
- Verified a real 12-policy by 3-capital execution matrix as exactly 36 rows
  with zero passing policies.
- Added a fail-closed negative benchmark for missing policy combinations.

## V5.3.0 - 2026-09-02

Minor learned-objective neighborhood release.

- Added fail-closed OOF artifact audits for row counts, unique keys, fold-date
  isolation, finite predictions, artifact hashes and zero holdout leakage.
- Added a deterministic neighborhood audit across rank regression, pointwise
  tail classification and pairwise tail ranking.
- Required a feature-mechanism change when three structural objectives all
  have non-positive aggregate gross Sharpe.
- Verified the rule on three real failed objectives, a gross-positive control,
  an incomplete-report negative control and exact deterministic replay.
- Re-audited the active protocol, raw sources and all 1,214 materialized panel
  shards before promotion.

## V5.2.0 - 2026-09-02

Minor learned-model triage release.

- Added a deterministic audit separating full-rank IC from the performance of
  the actually traded prediction tails.
- Added explicit `rank_tail_mismatch`, `tail_instability`,
  `execution_cost_failure` and `proceed_capacity` classifications.
- Required structural objective changes after IC-positive/gross-negative
  failures instead of further tuning of the same ranked loss.
- Kept immutable OOF, net-quality and capacity requirements unchanged.

## V4.0.0 - 2026-09-02

Major execution-causality and reproducibility release.

- Removed next-session return availability and `target_tradable` from research
  and capacity target selection.
- Added counterfactual tests proving future outcome fields cannot change test
  portfolio weights.
- Added explicit evaluation/execution contract version 2 to generated reports
  and made the benchmark auditor reject legacy reports without it.
- Invalidated all pre-V4 factor-quality evidence produced by the affected
  evaluators; the prior S03 result fell from Sharpe 1.78 and +402% return to
  Sharpe -0.35 and -33% after correction.
- Made capacity aggregation deterministic across processes and verified exact
  SHA-256 equality on an independent full-matrix replay.
- Completed a four-factor, 15-fold, 120-row capacity benchmark with zero false
  survivors and 49 passing project tests.

## V3.1.0 - 2026-09-02

Minor capacity-completeness correction.

- Made quote-validity thresholds 0.5, 0.7 and 0.9 a required stress axis.
- Rejected the former fixed-threshold four-factor matrix as incomplete.
- Verified a replacement matrix with 30 rows and seven distinct policy
  configurations per factor.
- Preserved the V3.0 conclusion of zero full-development executable survivors.

## V3.0.0 - 2026-09-02

Major capacity-first survivor-selection release.

- Separated diagnostic completeness, formal input completeness, research
  quality, executable capacity survival and formal promotion eligibility.
- Required one intact capacity policy to pass every capital tier before a
  factor can become an executable development survivor.
- Prevented one-axis frontier values from being combined without a rerun.
- Reclassified the full four-factor suite from one research-quality survivor
  to zero executable survivors while retaining a positive short-panel control.
- Added an unconstrained-engine equivalence test and a missing-capacity-row
  fault test.

## V2.2.0 - 2026-09-02

Minor data-admission release.

- Added a fail-closed materialized-panel audit before full backtests.
- Verified the complete 2019-2022 plus 2024 panel: 1,214 dates, 2,394,782
  rows, one schema and no holdout dates.
- Recomputed every shard content hash and reconciled all source-date and
  materialization-ledger records.
- Added negative tests that reject a missing date and a tampered content hash.

## V2.1.0 - 2026-09-02

Major experiment-control and evidence-integrity release.

- Added hard wall-clock and artifact-storage budgets with fail-closed preflight.
- Added bar1m manifest/schema/date audits and hsjday binary-integrity audits.
- Added suite-level completeness checks across walk-forward and capacity stress.
- Separated diagnostic completion from formal promotion eligibility.
- Required real point-in-time membership and exact security-status inputs for
  formal backtest promotion.
- Verified four representative factors, 16 walk-forward folds and 96 capacity
  rows without changing their factor metrics.
- Added fault-injection checks for storage overflow and missing benchmark tasks.

## V1.0.0 - 2026-09-02

Initial stable Skill release.

- Added active data-protocol auditing and split-drift detection.
- Added resumable champion/challenger factor-trial checkpoints.
- Added capacity, fill, Sharpe, diversity and evidence-level gates.
- Added autonomous branch stopping and cross-turn resume rules.
- Separated Skill versions (`Vn`) from factor/model trials (`Tnnn`).
- Excluded BigQuant AIStudio submission-file compliance review.
