# Model Specification Neighborhood

Use this audit after a label horizon, smoothing span, feature window or similar
ordered model specification has been searched. It prevents one attractive
development point from being promoted when nearby specifications fail.

Predeclare at least three ordered axis values. Keep the structural model
contract, data protocol, features, seed, cost convention and quality thresholds
fixed. Declare mechanically linked fields, such as an EMA span paired with a
target horizon, so they are excluded from the structural signature without
hiding unrelated model changes.

Run `scripts/audit_model_specification_neighborhood.py` on every report. A
neighborhood passes only when at least one adjacent pair clears the complete
quality gate. A single passing point is isolated and remains diagnostic. When
all points fail, mark the neighborhood exhausted and move to a materially
different causal representation; do not fill in ever-denser intermediate
values.

The audit never replaces individual hard gates or capacity evaluation. It adds
a selection-bias gate before capacity.
