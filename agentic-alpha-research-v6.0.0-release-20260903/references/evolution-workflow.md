# Evolution Workflow

## 1. Freeze the Experiment Contract

Record before evaluation:

- protocol ID and data manifests;
- parent factor or model ID;
- economic hypothesis;
- label, decision time and holding horizon;
- train/test folds, purge and embargo;
- costs, capacity tiers and fill assumptions;
- primary objective, hard gates and compute budget;
- random seeds and software version.

Do not change this contract while comparing siblings.

## 2. Establish T001

Reproduce the parent under the active protocol. A parent that cannot be
reproduced is not a valid champion. Separate pipeline failures from weak alpha.

## 3. Create One Falsifiable Change per Trial

Examples:

- change a causal window or normalization because stability decays;
- add a downside or regime head because a named state fails;
- replace a loss because tail observations dominate;
- reduce concentration because capacity fails;
- add a distinct feature family because the archive has coverage debt.

Avoid changing the label, features, model, portfolio construction and costs in
one generation. That destroys attribution.

## 4. Evaluate Identically

Use the same walk-forward folds and execution assumptions for every sibling.
Report fold metrics, yearly metrics, pressure states, turnover, cost sensitivity
and capacity. Run deterministic repeats when training is stochastic.

## 5. Diagnose

Classify rejection as one or more of:

- causal or data-contract failure;
- insufficient coverage;
- weak mean signal;
- unstable folds or years;
- risk concentration or drawdown;
- cost or turnover failure;
- capacity or fill failure;
- structural or behavioral duplication;
- stochastic instability;
- protocol incompatibility.

The next trial must address a diagnosed failure rather than introduce
unrelated complexity.

## 6. Promote or Retain

Use champion/challenger selection. A challenger must pass all hard gates and
improve the declared objective by a material margin. Preserve the previous
champion when evidence is ambiguous. A rejected experiment remains in the
ledger but is excluded from deliverable candidates.

## 7. Persist State

Store a compact generation record containing:

```text
run_id, protocol_id, trial_id, parent_id, candidate_id, hypothesis,
config_hash, seed, metrics, gate_decision, rejection_reasons, artifact_paths
```

Keep append-only lineage and immutable raw metrics. Derived summaries may be
rebuilt; evidence must not be overwritten.

## 8. Continue Across Cycles

Treat T001-T003 as the first diagnostic cycle. If T002 or T003 reveals a new
actionable failure mode, begin T004 from the current champion, then continue
T005, T006 and beyond. At each cycle boundary write a compact checkpoint with the champion,
open hypotheses, exhausted branches and next evaluation budget. Resume from
that checkpoint in later turns. Never renumber from T001 or discard failed-branch
memory merely because the conversation changed.

`Vn` is reserved for Skill versions and must never identify a factor trial.
