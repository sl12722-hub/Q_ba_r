# Backtest Completeness Contract

## Diagnostic Suite

A diagnostic suite is complete only when all declared representative factors
have:

- causal AST validation;
- identical purged walk-forward settings and the expected number of folds;
- finite IC, ICIR, Sharpe, worst-fold IC, turnover, coverage and return;
- the full declared capital, quantile, participation, cost and fill matrix;
- protocol and source-audit hashes;
- explicit research and execution causality-contract versions;
- transaction-cost contract version 3 or newer, with full one-way traded
  notional divided by prior NAV as turnover;
- for learned models, immutable OOF predictions with unique fold/date/instrument
  keys, non-overlapping test dates and a fixed prediction direction;
- explicit evidence label and rejection reasons.

Short panels or unfiltered universes remain `diagnostic_only` even when every
metric is strong.

## Formal Promotion Backtest

In addition to the diagnostic contract, formal promotion requires:

- real point-in-time target-universe membership;
- real point-in-time suspension, ST and exact upper/lower price-limit inputs;
- complete development coverage under the active split;
- no `--allow-unfiltered-universe` bypass;
- transaction-cost and capacity stress across every required capital tier;
- identical cost units and portfolio policy between research and capacity
  engines;
- no missing fold, year or required stress case;
- a frozen candidate before any isolated holdout evaluation.

Synthetic plumbing fixtures may test code paths but can never satisfy these
requirements. If any required input is absent, report the diagnostic metrics
but set formal promotion to blocked.

## Isolated Holdout

The 2023 regime holdout is not a search oracle. Consume it only for a frozen
candidate and record the access in the audit ledger. Do not change direction,
features, thresholds, model or portfolio policy from its result. Training
includes 2024, so label this result `regime_holdout_result`, not chronological
forward OOS.
