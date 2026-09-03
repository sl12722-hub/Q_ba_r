# Transaction-Cost Accounting

Use one explicit convention throughout the factory:

`turnover_t = sum_i(abs(target_notional_i - current_notional_i)) / prior_nav`

With a market-neutral portfolio whose long and short books are each 100% of
NAV, initial deployment has turnover 2.0. A one-way cost of 10 bps therefore
creates a 20 bps initial drag when fully filled. Do not multiply half-turnover
by a one-way cost.

## Required Checks

- Store `turnover_accounting=full_one_way_traded_notional_over_nav` in research
  contract version 3 or newer.
- Capacity PnL must deduct `abs(executed_notional) * one_way_cost`.
- Reset positions at a fold boundary and charge the next fold's opening trades.
- A non-rebalance session must retain positions and execute zero intentional
  orders; do not silently rebalance to stale target weights.
- Treat earlier net returns, Sharpe, capacity decisions and champions using a
  half-turnover convention as invalid and rerun them.

Gross results may diagnose signal, but they cannot pass a net quality or
capacity gate.
