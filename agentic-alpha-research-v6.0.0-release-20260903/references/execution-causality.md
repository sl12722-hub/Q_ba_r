# Execution Causality Contract

Separate target construction from order execution.

- Build the target portfolio only from fields known at the declared decision time.
- A next-session return, fill outcome, suspension flag, price-limit outcome or
  `target_tradable` value may evaluate or constrain execution, but may not
  change which instruments are selected.
- Historical labels inside a completed training fold may set factor direction;
  test-period outcome fields may not affect test-period target weights.
- Signal-quality evaluation must also form test portfolios before inspecting
  target availability. If a selected tail lacks a return, mark that portfolio
  observation incomplete instead of silently replacing the selected security.
- Keep an explicit regression test that perturbs future returns and execution
  flags while holding decision-time inputs fixed. The target weights must remain
  byte-for-byte identical.

Treat any violation as a causality failure. Invalidate affected capacity
results and rerun them after the engine is corrected.
