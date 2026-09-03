# Model Fold Concordance

An ensemble diversifies variance only when its members fail differently. Before
tuning weights, compare the OOF fold-IC vectors under one complete experiment
contract.

Run `scripts/audit_model_fold_concordance.py` with the member research reports
and the fixed, predeclared ensemble report.

Close the weighting branch when all of the following hold:

1. every member has the same fold set;
2. mean pairwise member fold-IC correlation exceeds the declared threshold;
3. every member breaches the same worst-fold floor in at least one fold;
4. the fixed ensemble also breaches that fold and does not repair it.

Do not search weights after closure. That search uses the observed OOF failure
to optimize the same observations and turns one structural miss into selection
bias. Change the causal representation, feature mechanism or data source.

Fold concordance is a diagnostic, not promotion evidence. A non-closed branch
still requires the full quality and capacity gates.
