# GPU OOF Model Execution

## Training Contract

- Prefer CUDA for dense neural training and record the device and GPU name.
- Fit preprocessing statistics on the training fold only.
- Construct labels within the training fold. Drop incomplete forward-horizon
  labels rather than borrowing targets from purge or test rows.
- Use deterministic seeds and deterministic CUDA algorithms when supported.
- Preserve architecture, loss, optimizer, sample cap, batch size, features,
  label horizon and every fold's training loss.

## OOF Prediction Contract

Write one immutable table containing `fold_id`, `date`, `instrument`, `factor`,
`target`, `target_tradable` and the decision-time liquidity proxy. Require:

- unique fold/date/instrument keys;
- no date appearing in more than one test fold;
- the expected fold and date counts;
- a SHA-256 hash in downstream manifests;
- direction fixed by the trained model, never relearned from OOF targets.

## Complete Evaluation

1. Compute fold and aggregate IC, ICIR, gross and net Sharpe, total return,
   worst-fold IC, coverage and full-notional turnover.
2. Diagnose holding feasibility with causal exit buffers or scheduled
   rebalancing. Non-rebalance days must not create target-reset trades.
3. Run capacity directly from fixed OOF predictions at every capital tier and
   declared stress axis.
4. Keep a model as a predictive research lead when IC is strong but net or
   capacity gates fail; do not call it an executable survivor.

Do not use the isolated 2023 regime holdout to choose architecture, label,
portfolio buffer, rebalance schedule or capacity policy.
