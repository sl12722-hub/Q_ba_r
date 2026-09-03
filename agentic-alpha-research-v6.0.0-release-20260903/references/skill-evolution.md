# Skill Self-Evolution Protocol

## Version Namespace

- Skill versions: `V1`, `V2`, `V3`, ...
- Factor/model trials: `T001`, `T002`, `T003`, ...
- Experiment runs: immutable run IDs or hashes

Legacy S04 records labeled V1-V22 predate this namespace. Interpret them as
factor trials T001-T022; they do not imply 22 Skill versions.

## Stable and Candidate Versions

Keep one stable Skill and at most one active candidate. A candidate version may
change instructions, scripts, schemas, research policies, orchestration,
resource handling or reporting. Merely producing another factor is not a Skill
change.

Before editing, write a hypothesis explaining which observed Skill failure the
change should fix. Keep the stable version reproducible so the candidate can be
compared against it.

## Benchmark Suite

Use several representative workloads when available:

- one deterministic expression factor;
- one capacity- or turnover-sensitive factor;
- one weak or unstable factor that should be rejected correctly;
- one ML/DL task when GPU training is part of the candidate change.

Run stable and candidate Skills under the same protocol, factor inputs, compute
budget and evaluation gates. The factors are test fixtures for Skill quality,
not Skill versions.

## Promotion Criteria

A candidate must not regress any safety invariant. Evaluate:

- protocol and leakage violations;
- reproducibility and resume correctness;
- false promotions and false rejections;
- development evidence quality and fold stability;
- diversity of accepted mechanisms;
- compute time, peak RAM, CPU pressure and GPU utilization;
- completeness of manifests, lineage and rejection diagnosis;
- number of external or holdout looks consumed.

Promote only when the candidate has a material, attributable advantage on the
declared objective and no critical regression. Otherwise retain the stable
Skill, record the failed hypothesis, and design another candidate.

## Release Record

For each Skill version store:

```text
skill_version, parent_version, status, hypothesis, changed_files,
benchmark_tasks, benchmark_artifacts, promotion_decision, known_limits
```

Update `VERSION` and `CHANGELOG.md` only after promotion. Candidate experiments
belong in a separate workspace or versioned artifact directory.
