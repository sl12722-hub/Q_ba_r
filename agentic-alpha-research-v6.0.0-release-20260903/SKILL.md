---
name: agentic-alpha-research
description: Evolve, test, diagnose, and document factors or ML/DL strategies in the local Agentic Alpha research factory. Use for factor mining, strategy iteration, walk-forward evaluation, capacity stress, low-correlation selection, experiment retrospectives, and champion/challenger promotion. Do not use for BigQuant AIStudio notebook compliance or submission-file review.
---

# Agentic Alpha Research

Operate the local factor factory as an evidence-driven research loop. The skill
is the orchestration and research-policy layer; data processing, GPU training,
factor execution and backtesting remain in the project.

## Start Here

1. Locate the project using [references/local-project.md](references/local-project.md).
2. For autonomous work, initialize `scripts/run_guard.py` and check it before
   and after every materialization, training, search or backtest job. Do not
   start work that would exceed its wall-clock or artifact reservation.
3. Run `scripts/protocol_doctor.py` before a new experiment or after any split,
   configuration or data-path change.
4. Run `scripts/data_source_audit.py` before accepting a new source snapshot.
5. After materialization, run `scripts/audit_materialized_panel.py` using
   [references/panel-audit.md](references/panel-audit.md). Do not start a full
   backtest until the exact expected date set, lineage metadata, schema, keys,
   ledger and recomputed content hashes all pass.
6. Read [references/data-protocol.md](references/data-protocol.md) before loading
   dates, panels, archives or prior trajectories.
7. Select the appropriate mode below and execute it end to end.
8. Before capacity evaluation, enforce
   [references/execution-causality.md](references/execution-causality.md). Target
   selection must not inspect next-session returns or execution outcomes.
9. Before interpreting any cost-adjusted result, enforce
   [references/transaction-cost-accounting.md](references/transaction-cost-accounting.md).
   Research and capacity engines must use the same full one-way traded-notional
   convention.
10. For GPU or other learned models, read
    [references/gpu-oof-execution.md](references/gpu-oof-execution.md). Preserve
    fold-fixed OOF predictions and evaluate their capacity without relearning
    direction from OOF targets.
11. Before comparing or ensembling learned trials, enforce
    [references/complete-experiment-contract.md](references/complete-experiment-contract.md).
    Record the complete walk-forward, portfolio, evaluation and model contract;
    reject attractive metrics from incompletely recorded or mismatched trials.
12. When several windows, weights, architectures or portfolio thresholds are
    searched, enforce
    [references/selection-bias-control.md](references/selection-bias-control.md).
    A lone threshold crossing after local tuning is not robust evidence.
13. For learned models, audit mean-rank skill against the actually traded
    tails using [references/model-tail-alignment.md](references/model-tail-alignment.md).
    Preserve concurrent failure modes. Stop loss-weight tuning when positive IC
    coexists with non-positive gross portfolio Sharpe; do not call a model a
    cost failure when net performance passes but rank or worst-fold gates fail.
14. Before tuning ensemble weights, audit member fold concordance with
    [references/model-fold-concordance.md](references/model-fold-concordance.md).
    Close the weighting branch when highly concordant members fail the same
    fold and the fixed ensemble preserves or worsens that failure.
15. After closing a static-level model branch for shared fold failure, consider
    [references/causal-rank-innovation.md](references/causal-rank-innovation.md).
    Test pure innovation before a level-plus-innovation hybrid and require an
    ordered lag neighborhood; this is a mechanism change, not a default recipe.
16. After testing several materially different learned objectives, apply
    [references/model-objective-neighborhood.md](references/model-objective-neighborhood.md).
    Audit every OOF artifact, then close an exhausted objective neighborhood
    instead of tuning its siblings.
17. When an ordered learned-model specification is searched, apply
    [references/model-specification-neighborhood.md](references/model-specification-neighborhood.md).
    A lone passing horizon or smoothing span is not promotion evidence.
18. When execution axes may interact, distinguish a one-axis frontier from a
    complete Cartesian grid using
    [references/cartesian-capacity-audit.md](references/cartesian-capacity-audit.md).
19. For fixed OOF predictions and multi-policy capacity work, use the
    GPU-batched executor under
    [references/gpu-capacity-execution.md](references/gpu-capacity-execution.md).
    Admit it only after a CPU parity control on the same immutable OOF artifact.
20. Require the exact research portfolio as a capacity anchor using
    [references/research-policy-capacity-anchor.md](references/research-policy-capacity-anchor.md).
    A stress grid that omits the research policy is incomplete, and an anchor
    near-miss remains a failed executable gate.

## Modes

- **Inspect:** explain the current factor, model, data coverage, lineage and
  evidence without changing it.
- **Evolve one factor:** create versioned challengers around one economic
  hypothesis, evaluate each generation, and retain a new champion only when it
  clears every hard gate.
- **Explore new mechanisms:** search distinct feature families or model classes,
  then enforce structural and behavioral diversity before admission.
- **Diagnose failure:** turn weak periods, cost sensitivity, low fill, unstable
  IC or excessive correlation into explicit next-round hypotheses.
- **Evolve a model strategy:** compare labels, architectures, losses or regime
  heads under the same frozen data protocol and compute budget.
- **Report:** summarize the strategy lineage, rejected branches, surviving
  evidence and unresolved risks. Report only survivors as deliverables while
  retaining rejection records for audit.

This skill does not inspect or certify BigQuant AIStudio submission notebooks.

## Evolution Loop

Follow [references/evolution-workflow.md](references/evolution-workflow.md).
For a single-factor request, use three trials as the first cycle, not as a
stopping limit. Reserve `Vn` exclusively for Skill versions; name factor/model
trials `T001`, `T002`, and so on:

1. Establish a reproducible T001 baseline.
2. Use T001 failure evidence to define one falsifiable T002 change.
3. Use T002 evidence to define one materially different T003 change.
4. Compare all trials on identical folds, costs, capacity tiers and data.
5. Promote only a challenger that passes the hard gates and improves the
   declared primary objective without violating risk or diversity constraints.
6. Start the next cycle from the surviving champion and the accumulated failure
   diagnosis. Continue trial numbering across turns instead of restarting.
7. Record every attempted sibling in a mechanism family. Keep only one family
   representative, and require neighborhood or perturbation stability before
   promoting a tuned parameter point.

Use `scripts/select_challenger.py --checkpoint-input <prior.json>` when a prior
cycle exists. Supply `--new-hypothesis` only when changing to a genuinely new,
falsifiable branch; this resets the branch failure count but preserves the full
generation history, champion and exhausted branches. Always write a new
checkpoint file instead of mutating the prior record.

Never label a generation as improved merely because it is newer, more complex,
or has a better in-sample metric. Do not combine separately optimized parameter
axes without rerunning the combined policy.

## Skill Self-Evolution

Read [references/skill-evolution.md](references/skill-evolution.md). The current
stable version is stored in `VERSION`; Skill versions are independent of factor
trial counts. Create a new Skill version only when its instructions, policies,
scripts, state schema, evaluation logic or orchestration behavior changes.
Use [references/benchmark-suite.md](references/benchmark-suite.md) when comparing
a stable Skill with a candidate.

Benchmark each Skill candidate on several representative factors or model
tasks. Promote the candidate only when it improves research quality or
efficiency without weakening causality, leakage prevention, reproducibility,
resource control or evidence labeling. A Skill candidate may run any number of
factor trials before its promotion decision.

## Required Invariants

- Enforce the active date split and its non-chronological warning.
- Never join labels across an excluded calendar gap.
- Do not seed a run from archives or trajectories created under an incompatible
  protocol.
- Keep future returns, leaderboard feedback and holdout metrics out of proposal,
  training, hyperparameter selection and direction selection.
- Prefer GPU for dense model training and batched tensor work. Keep tabular I/O,
  group-by work and diagnostics bounded to one worker unless profiling supports
  a higher setting.
- Run Cartesian capacity policies as one float64 GPU batch when the dense panel
  fits memory. Keep CPU threads at one, report wall time, process CPU time and
  peak CUDA allocation, and fall back to chunked GPU batches before considering
  a multi-worker CPU replay.
- Use typed fields and causal ASTs. A valid file or expression is not evidence
  of alpha quality.
- Distinguish smoke tests, local diagnostics, admissible development evidence,
  isolated holdout evidence and external official results.
- Never promise a leaderboard score or present a local score as an official
  score.
- Apply the gates in [references/quality-gates.md](references/quality-gates.md).
- Apply [references/capacity-first-selection.md](references/capacity-first-selection.md)
  before naming any development survivor. A complete capacity table is not a
  passed capacity gate; require one intact policy configuration to clear every
  capital tier without combining separately optimized axes.
- Preserve experiment manifests, seeds, configuration hashes, parent IDs,
  metrics and rejection reasons.
- Read [references/backtest-contract.md](references/backtest-contract.md) before
  calling a backtest complete or a factor promotion-eligible.
- Invalidate and rerun capacity evidence if future execution fields influenced
  target selection, even when the affected report otherwise passed every gate.
- Invalidate cost-adjusted evidence produced with half-turnover multiplied by a
  one-way cost. Initial 100% long plus 100% short deployment has traded-notional
  turnover 2.0, not 1.0.
- Treat model IC and gross Sharpe as predictive diagnostics, not executable
  evidence. Learned-model promotion requires immutable OOF predictions, a
  complete net research report and a precomputed-prediction capacity frontier.
- Do not compare, average or select learned trials unless every report records
  the complete evaluation, walk-forward, portfolio and model contract. Purge,
  embargo, minimum training length, test length, portfolio quantile and cost
  are selection-relevant fields, not incidental metadata.
- A high-scoring trial with a missing or mismatched contract is inadmissible.
  Keep it as a protocol counterexample and rerun under the intended contract.
- Do not tune ensemble weights when member fold-IC vectors are highly
  concordant, every member breaches the same fold floor and the fixed ensemble
  does not repair that fold. Change the causal representation or feature
  mechanism instead.
- When a pure causal innovation representation repairs worst-fold stability but
  loses mean rank signal, a predeclared level-plus-innovation hybrid is a valid
  next hypothesis. Require at least one adjacent passing lag pair.
- Capacity evidence must include the exact research-policy anchor: entry tail,
  exit tail, daily rebalance, cost convention and every capital tier. Do not
  lower fill, Sharpe or return gates to rescue an anchor near-miss.
- Do not send a learned model to capacity merely because mean IC is positive.
  Run `scripts/audit_model_tail_alignment.py`; distinguish rank-tail mismatch,
  cross-fold tail instability and execution-cost failure before choosing the
  next experiment.
- Treat regression, pointwise tail classification and pairwise tail ranking as
  structural objective families. When all three have non-positive aggregate
  gross Sharpe under the same feature mechanism, record objective-neighborhood
  exhaustion and change the causal representation.
- Require an adjacent passing pair before selecting an ordered model horizon,
  window or smoothing specification. Close an all-failed neighborhood instead
  of adding post hoc intermediate points.
- Aggregate representative factor runs with `scripts/benchmark_audit.py`. A
  collection of individually successful commands is not a complete suite.
- Do not describe a deduplicated one-axis capacity frontier as a Cartesian
  execution matrix. Require every fixed policy combination and every capital
  tier to pass `scripts/audit_capacity_cartesian.py`.
- A faster capacity engine is not trusted by construction. Require exact policy
  keys and trading-day counts plus numerical parity for return, Sharpe, fill,
  exposure and traded notionals against a bounded CPU control before using its
  output for candidate selection.

## Autonomous Stopping

Continue without requesting routine confirmation when the user authorizes an
autonomous experiment. Three generations are only a minimum diagnostic cycle.
Continue until the user stops the run or one of these conditions occurs:

- an explicit compute, time or evaluation budget is exhausted;
- three consecutive generations fail and no new falsifiable hypothesis can be
  derived from their distinct failure modes;
- the data protocol, causality contract or deterministic tests fail;
- no challenger clears every hard gate;
- further work requires new external data, credentials, paid services or user
  authorization.

Do not hide an unsuccessful run. Conclude that no challenger was promoted,
record why, and leave the previous champion unchanged.
