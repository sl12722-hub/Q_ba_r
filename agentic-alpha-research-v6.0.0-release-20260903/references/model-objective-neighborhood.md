# Model Objective Neighborhood

Use this protocol after a learned factor has positive mean IC but its traded
prediction tails fail. The purpose is to distinguish a repairable objective
mismatch from an exhausted feature mechanism.

## Minimum Structural Neighborhood

Evaluate at least three materially different training objectives on identical
walk-forward folds, features, costs and portfolio rules:

1. full-rank regression or a rank-weighted regression baseline;
2. pointwise upper-versus-lower tail classification;
3. pairwise upper-tail versus lower-tail ranking.

Changing only a tail quantile, learning rate, network width, seed or loss
constant is a sibling, not a new objective family.

Before aggregating objectives, run `scripts/audit_model_oof_artifact.py` on
each report. Require matching report/artifact row counts, unique date/instrument
keys, one test fold per date, finite predictions and zero isolated-holdout rows.

## Exhaustion Rule

Run `scripts/audit_model_objective_neighborhood.py` on the immutable research
reports. Mark the objective neighborhood exhausted when all conditions hold:

- at least three distinct objective families are complete;
- every report contains the same evaluation and OOF contracts;
- no objective has positive aggregate gross Sharpe;
- no objective is capacity eligible under the tail-alignment audit.

After exhaustion, stop target and optimizer tuning for that feature mechanism.
Move to a different causal feature representation, economic mechanism or
portfolio head. Preserve the failed reports as negative evidence.

An objective neighborhood is a development diagnostic. It cannot waive the
data-source, holdout, transaction-cost, capacity or formal-input gates.
