# Local Project

Configure these locations for the machine that runs the research factory. Do
not commit credentials, private data, or machine-specific secrets.

## Project Root

Set an environment variable that points to the existing research project:

```powershell
$env:AGENTIC_ALPHA_PROJECT_ROOT = "C:\path\to\agentic_alpha_cleanroom"
```

The project should contain its own source package, configuration, factor
engine, backtester, and artifact directories. The skill does not duplicate
those components.

## Python Environment

```powershell
$env:AGENTIC_ALPHA_PYTHON = "C:\path\to\.venv\Scripts\python.exe"
```

Set `PYTHONPATH=src` when running package modules without an editable install.

## Data Roots

Configure project-local paths or environment variables for each admitted data
source, for example:

```powershell
$env:AGENTIC_ALPHA_MINUTE_ROOT = "D:\data\stock_bar1m"
$env:AGENTIC_ALPHA_FEATURE_ROOT = "D:\data\feature_lake"
$env:AGENTIC_ALPHA_DAILY_ROOT = "D:\data\daily_context"
```

Record immutable source manifests and hashes in the project. Treat row-count,
date-count, schema, or content-hash changes as a data-version event.

## Baseline Verification

From the configured project root:

```powershell
Set-Location $env:AGENTIC_ALPHA_PROJECT_ROOT
$env:PYTHONPATH = "src"
& $env:AGENTIC_ALPHA_PYTHON -m unittest discover -s tests -v
& $env:AGENTIC_ALPHA_PYTHON -m agentic_alpha doctor --config configs/project.toml
```

Update the expected development and isolated-holdout date counts in the project
configuration. Never silently accept a changed snapshot.

