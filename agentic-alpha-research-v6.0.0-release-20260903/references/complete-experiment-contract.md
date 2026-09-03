# Complete Experiment Contract

Learned-trial comparison is valid only when every selection-relevant setting is
recorded. Headline metrics and identical filenames are not a contract.

Require these sections in every research report:

- `evaluation_contract`: decision-time selection, future-field exclusion and
  turnover convention;
- `walkforward_contract`: minimum training days, test days, purge days and
  embargo days;
- `portfolio_contract`: tail quantile, minimum cross-section and one-way cost;
- `model_contract`: features, representation, target, architecture, seed,
  training window, smoothing and all estimator parameters.

Before comparison or ensembling:

1. Run `scripts/audit_experiment_contract.py` on every source report.
2. Permit differences only for the predeclared model axis under study, such as
   `seed` or `train_lookback_days`.
3. Require exact equality for all other contract fields.
4. Require exact OOF key and outcome parity in the project ensemble builder.
5. Reject a batch when some reports contain a contract section and others do
   not. Legacy omission is not evidence of equality.

Never infer purge, embargo or portfolio settings from scores. A passing trial
with an incomplete contract is a protocol counterexample and must be rerun.
