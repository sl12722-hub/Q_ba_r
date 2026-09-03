# Capacity-First Selection

Treat idealized walk-forward quality and executable capacity as separate gates.
The quality evaluator may reconstruct a friction-adjusted portfolio each day;
the capacity evaluator carries positions, enforces liquidity participation and
retains positions that cannot trade. Large differences between the two are an
execution diagnosis, not automatically an engine error.

Before naming a `development_survivor`:

1. Require the declared walk-forward quality gate to pass.
2. Require the complete capital and stress matrix.
3. Group capacity rows by the full policy tuple: tail quantile, participation
   rate, one-way cost and quote-validity threshold.
4. Accept a policy only when every required capital tier passes return, Sharpe
   and fill gates. Never combine the best value from separate one-axis cases.
5. Keep point-in-time membership and exact security-status requirements as a
   separate formal-promotion gate.

Use `scripts/benchmark_audit.py` to distinguish diagnostic completeness,
formal input completeness, research-quality acceptance, executable diagnostic
survival and formal promotion eligibility.

A factor can be diagnostically complete and still have no executable survivor.
That outcome is a valid rejection, not an incomplete run.
