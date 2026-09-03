# Materialized Panel Audit

Run `scripts/audit_materialized_panel.py` after materialization and before any
full-development backtest. The audit derives the expected source-date set from
the active project configuration and time firewall. It fails closed on:

- missing or extra dates, including accidental holdout admission;
- output paths, file names or source metadata that disagree with the date;
- missing lineage metadata or unexpected source file names;
- empty shards, duplicate `(date, instrument)` keys or multiple dates per shard;
- schema drift, infinite numeric values or content-hash mismatch;
- incomplete or malformed materialization ledgers.

Use `--expected-dates-file` only for isolated regression fixtures. A formal
development audit must omit this option so the complete active split is
derived from the project configuration. Preserve the JSON report and include
its SHA-256 in the benchmark manifest.

Materializer versions may differ only when the recomputed canonical content
hash and schema both pass. Version labels are lineage, not substitutes for
content verification.
