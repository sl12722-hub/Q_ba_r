# Agentic Alpha Research Skill V6.0.0

English | [简体中文](README_CN.md)

An evidence-driven Codex skill for evolving and auditing local quantitative
factor and ML/DL research workflows.

The skill is an orchestration and research-policy layer. It does not bundle
market data, trained models, proprietary factor outputs, or a trading engine.
It is designed to sit above an existing research project and enforce causal,
reproducible promotion decisions.

## V6.0 Highlights

- Complete experiment-contract checks before model comparison or ensembling.
- Fold-concordance diagnostics that close unproductive ensemble-weight searches.
- Causal rank-innovation routing after shared static-level model failure.
- Ordered-neighborhood checks for horizons, lags, and smoothing specifications.
- Immutable OOF artifact, tail-alignment, and objective-neighborhood audits.
- GPU-oriented Cartesian capacity evaluation with required CPU parity controls.
- Exact research-policy capacity anchors across all declared capital tiers.
- Fail-closed promotion: strong diagnostics are not called executable evidence
  when capacity, causality, data, or reproducibility gates fail.

## Repository Layout

```text
agentic-alpha-research/
|-- SKILL.md
|-- VERSION
|-- CHANGELOG.md
|-- agents/openai.yaml
|-- references/
|-- scripts/
|-- tests/
`-- docs/PROMOTION_EVIDENCE_V6.0.md
```

## Install as a Codex Skill

Copy the contents of this release package to:

```text
%USERPROFILE%\.codex\skills\agentic-alpha-research
```

Keep the installed folder name `agentic-alpha-research`, with `SKILL.md` at its
top level. Restart or reload Codex after installation. The skill remains
eligible for automatic invocation and can also be invoked explicitly as
`$agentic-alpha-research`.

## Connect a Research Project

Edit `references/local-project.md` and set the project, Python environment, and
data locations for your machine. The project is expected to provide its own
factor engine, backtester, model dependencies, and `agentic_alpha` package.

The standalone audit helpers use Python 3.11+ standard-library modules where
possible. Panel and OOF audits additionally require the project environment,
including `numpy`, `pandas`, and `pyarrow`.

## Validate

From the repository root:

```powershell
python -m unittest discover -s tests -v
python path\to\skill-creator\scripts\quick_validate.py .
```

The promoted V6.0 candidate passed 16 skill tests and 70 project tests in its
recorded development environment. See
`docs/PROMOTION_EVIDENCE_V6.0.md` for the promotion rationale and rejected
capacity near-miss.

## Scope

This repository supports research workflow quality; it does not promise
investment performance or leaderboard scores. Local diagnostic metrics are not
official platform results. BigQuant AIStudio submission-file compliance is
deliberately outside this skill's scope.

## Release Integrity

`MANIFEST.sha256` records every release file. Verify the downloaded repository
before installation when distributing it outside GitHub's normal clone flow.
