# Research-Policy Capacity Anchor

Capacity evaluation must include the exact policy used by the research report,
not only slower or wider execution stresses.

For the current long-short research evaluator, the anchor is:

- entry quantile equal to `portfolio_contract.quantile`;
- exit quantile equal to the entry quantile;
- rebalance every decision day;
- one-way cost equal to `portfolio_contract.one_way_cost_bps`;
- every declared capital tier.

Run `scripts/audit_research_policy_anchor.py` on the anchor frontier. Missing or
duplicate capital tiers fail closed. The anchor is executable only if every
capital tier passes the unchanged return, Sharpe and fill gates.

Keep slower rebalance and wider exit policies as a separate stress grid. Do not
replace the missing anchor with the best stress point, and do not relax a gate
because the anchor is close.
