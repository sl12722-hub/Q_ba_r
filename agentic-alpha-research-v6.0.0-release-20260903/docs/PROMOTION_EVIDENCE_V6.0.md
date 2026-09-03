# V6.0 Promotion Evidence

## Decision

Promote `agentic-alpha-research` V6.0.0 as a major workflow release. The Skill
learned a new causal-representation route and a stricter capacity-anchor
contract. No factor is promoted because capacity fill remains below the fixed
gate.

## Representation Transition

The static-level XGBoost memory ensemble had mean pairwise fold-IC correlation
0.892391, and every member failed fold 12. The fixed ensemble worsened that fold
to -0.016165, so V5.9 closed weight tuning.

T183 used pure 5-day cross-sectional rank innovation. It repaired worst-fold IC
to -0.007971 but reduced mean IC to 0.008211, so it failed the quality gate.
This supported the predeclared level-plus-innovation hypothesis.

| Trial | Innovation lag | IC | ICIR | Net Sharpe | Return | Worst-fold IC | Quality |
|---|---:|---:|---:|---:|---:|---:|---|
| T185 | 3 | 0.014183 | 3.017 | 2.949 | 3.410 | -0.005448 | pass |
| T184 | 5 | 0.014939 | 3.205 | 2.949 | 3.161 | -0.005450 | pass |
| T186 | 10 | 0.014031 | 3.021 | 3.147 | 3.738 | -0.003361 | pass |

The ordered neighborhood has three accepted points and two adjacent passing
pairs. T186's OOF artifact passed: 1,921,298 rows, 945 dates, 15 folds, no
duplicate keys, no fold-date overlap, no non-finite prediction and zero 2023
rows. Tail alignment classified it as `proceed_capacity`.

## Capacity Outcome

The 12-policy by 3-capital GPU stress grid was complete and evaluated in 3.67
seconds, but accepted zero fixed policies. The best stress policy reached about
Sharpe 1.87, below the unchanged 2.0 gate.

The exact daily research anchor was then evaluated at 100k, 500k and 1m:

| Capital | Total return | Sharpe | Fill | Gate |
|---:|---:|---:|---:|---|
| 100,000 | 6.310 | 3.207 | 0.892481 | fail |
| 500,000 | 6.272 | 3.199 | 0.892437 | fail |
| 1,000,000 | 6.263 | 3.196 | 0.892477 | fail |

All tiers failed only the fixed 0.90 fill gate. The gate was not relaxed.

## Validation

- Skill tests: 16 passed.
- Project tests: 70 passed.
- Skill quick validation: passed.
- Anchor audit deterministic replay SHA-256:
  `f981f4eb1b18c97154afabb78ac19eca42cc0f3becca5e498e66b55a73c864a3`.
- Training and dense capacity execution used CUDA; CPU numerical libraries were
  limited to one thread.
- 2023 remained untouched.
