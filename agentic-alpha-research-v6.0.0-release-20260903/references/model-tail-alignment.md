# Model Tail Alignment

Mean cross-sectional IC measures the full ranking. A long-short portfolio
trades only its tails, so positive IC can coexist with negative gross Sharpe.
Treat that combination as an objective mismatch, not as a cost or capacity
problem.

## Audit

Run `scripts/audit_model_tail_alignment.py` on the immutable OOF research
report before capacity evaluation. The report must contain aggregate IC,
aggregate gross and net Sharpe, the quality-gate decision, and fold-level gross
Sharpe values.

Classify the result before proposing another model. Preserve every applicable
failure mode; the first item is the primary diagnosis, not the only diagnosis:

- `rank_tail_mismatch`: mean IC is positive but aggregate gross Sharpe is not;
- `tail_instability`: gross Sharpe is positive but too few folds have positive
  gross Sharpe;
- `regime_concentration`: the worst-fold IC breaches the stability threshold;
- `execution_cost_failure`: net Sharpe, return or turnover fails its explicit
  threshold;
- `weak_rank_signal`: aggregate IC mean or IC IR is too weak even if the traded
  tails made money;
- `proceed_capacity`: tail alignment and the net development gate both pass.

## Response

For `rank_tail_mismatch`, stop tuning sample weights or hidden-layer widths on
the same ranked label. Change one structural element: use a tail-aware ranking
loss, a directly portfolio-aligned label, a separate tail head, or a causal
holding-period objective. Rerun fixed OOF evaluation from scratch.

For `tail_instability`, diagnose fold and regime concentration. Do not repair a
single bad fold by selecting a parameter on that fold; require neighboring
specifications to improve together under the selection-bias policy.

For `regime_concentration`, add only decision-time regime context and retest a
small neighboring specification set. A high aggregate return does not override
a failed worst-fold gate. For `weak_rank_signal`, change the representation or
label rather than treating tail profit as full-rank predictive evidence.

For `execution_cost_failure`, retain the model only as a predictive lead and
test causal holding, buffer or rebalance policies. Do not assign this label
merely because some unrelated quality gate failed. Capacity is warranted only
after a complete net research report passes.

Never use the isolated holdout, leaderboard feedback or future execution
outcomes to choose the label, loss, tail threshold or portfolio policy.
