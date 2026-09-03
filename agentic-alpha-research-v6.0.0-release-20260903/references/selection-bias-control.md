# Selection-Bias Control

Repeated development trials create selection optimism even when every single
backtest is causal. Preserve the full trial ledger and treat the number of
sibling attempts as evidence, not disposable search history.

## Family Search

- Define the economic mechanism before tuning windows, blend weights or
  portfolio thresholds.
- Keep all rejected siblings in the audit record.
- Deliver at most one representative from a closely related family.
- Do not promote a parameter that passes only at one isolated point while its
  adjacent windows or small perturbations fail materially.
- Prefer a slightly weaker center of a stable neighborhood to the best isolated
  development score.

For ordered learned-model specifications, enforce this rule with
[model-specification-neighborhood.md](model-specification-neighborhood.md).
Require at least one adjacent passing pair; do not densify an exhausted search
after observing its outcomes.

## Gate Interpretation

A hard-gate failure remains a failure even when it is numerically small. Do not
silently round, relax or replace the gate after observing results. A near miss
may justify one bounded diagnostic branch or a capacity diagnosis, but remains
`diagnostic_only` and cannot become a development survivor.

When a complementary factor is proposed to repair one bad fold, require an
economic rationale and test small predeclared weights. Stop the branch when the
complement lowers aggregate IC or merely moves the worst failure to another
fold.

## Portfolio Search

Do not combine the best quantile, participation rate, cost and data-quality
threshold from separate searches. One complete policy tuple must clear every
capital tier. Record the number of tried policies and report capacity failure
even when one capital tier has exceptional return.
