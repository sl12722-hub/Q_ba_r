# Quality Gates

Read the active project configuration first. The numbers below are defaults for
the current factory, not universal promises.

## Deterministic Hard Gates

- causal and eligible fields only;
- typed AST, valid units, node/depth budget and finite outputs;
- no target, holdout or leaderboard feedback in features or prompts;
- point-in-time membership and exact security status for promotion;
- valid protocol ID and compatible archive lineage;
- deterministic run manifest and complete metrics.

## Development Evidence

Current strict factor-search reference gates include at least six out-of-sample
folds, coverage 0.85, mean IC 0.015, ICIR 0.75, net Sharpe 1.0, non-negative
worst-fold IC and turnover no higher than 1.2. Read the live configuration and
report when it differs.

Do not optimize only mean IC. Include total return, worst year/fold, drawdown,
turnover, monotonicity and pressure-state behavior. A high aggregate result
cannot override a deterministic or stability failure.

## Capacity

Evaluate at least 100k, 500k and 1m capital with explicit one-way costs and
participation assumptions. For the current diagnostic policy:

- exploration floor: total return 10%, Sharpe 2.0, fill 90% at every tier;
- ordinary delivery reference: fill 95% at every tier;
- cost and quote-validity thresholds must be stressed, not fixed at the best
  observed point.

These short-sample capacity floors do not certify production quality.

Passing the development-quality gate does not override capacity failure. A
candidate becomes an executable diagnostic survivor only when at least one
complete policy tuple passes every capital tier. Keep baseline acceptance and
alternative-policy acceptance separate in reports.

## Diversity

Reject exact canonical duplicates, close subtree variants and candidates whose
absolute behavioral correlation exceeds the live archive threshold. Keep only
two or three best survivors per economic/model family when delivering a batch.

## Claims

Use these evidence labels exactly:

- `smoke_test`: verifies control flow only;
- `diagnostic_only`: missing a promotion input or full protocol coverage;
- `development_survivor`: passed active development gates;
- `regime_holdout_result`: evaluated on isolated 2023 without feedback;
- `external_result`: produced outside the local development protocol.

Never translate any local metric into an expected public or private leaderboard
score.
