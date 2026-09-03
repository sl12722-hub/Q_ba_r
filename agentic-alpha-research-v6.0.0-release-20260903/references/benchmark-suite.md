# Representative Skill Benchmark Suite

Use at least four workloads when the local archive supports them:

- a slow, lower-turnover price-path factor;
- a less stable or sign-sensitive factor;
- a quote-quality factor;
- a high-return but turnover- or capacity-sensitive factor.

Freeze the same panel, folds, costs, capitals and execution assumptions for the
stable and candidate Skill. Evaluate Skill behavior as well as factor metrics:

- source/protocol violations detected;
- incomplete backtests falsely called complete;
- weak factors falsely promoted;
- valid diagnostic jobs completed;
- deterministic rerun equality;
- elapsed time, artifact bytes and peak resource pressure;
- quality and specificity of rejection diagnoses.

Use `scripts/benchmark_audit.py` to verify suite completeness. A major Skill
version requires a structural capability change or a material cross-workload
gain with no critical regression. A one-factor parameter improvement is a
factor trial result, not evidence for a major Skill version.
