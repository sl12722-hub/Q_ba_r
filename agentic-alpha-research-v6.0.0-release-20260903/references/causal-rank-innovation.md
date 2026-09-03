# Causal Rank Innovation

Use this mechanism only after complete-contract static-level models show a
shared fold failure and fixed ensembling does not repair it.

For each decision-day feature:

1. apply the existing causal temporal transform using past observations only;
2. compute the decision-day cross-sectional rank;
3. subtract the same instrument's rank from a positive lag;
4. train and evaluate only with fold-fixed OOF predictions.

Start with a pure rank-innovation control. If it improves the worst fold but
loses mean IC, test a level-plus-innovation hybrid under the same model,
features, folds, costs and seed. Predeclare at least three ordered lags and use
the model-specification neighborhood audit. A lone passing lag is not evidence.

This is one causal-representation option, not a universal default. If pure
innovation does not improve the diagnosed failure, close the branch.
