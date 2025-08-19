## 📊 Status

[![CI](https://github.com/mvp-zplace/finance-ops-scripts/actions/workflows/ci.yml/badge.svg?branch=main&style=flat)](https://github.com/mvp-zplace/finance-ops-scripts/actions/workflows/ci.yml)
[![Smoke Test](https://github.com/mvp-zplace/finance-ops-scripts/actions/workflows/smoke-test.yml/badge.svg?branch=main&style=flat)](https://github.com/mvp-zplace/finance-ops-scripts/actions/workflows/smoke-test.yml)
[![Coverage Status](https://codecov.io/gh/mvp-zplace/finance-ops-scripts/branch/main/graph/badge.svg?token=8V8DVYQ9Z2&style=flat)](https://codecov.io/gh/mvp-zplace/finance-ops-scripts)

## 📄 Meta

![License](https://img.shields.io/badge/license-MIT-informational?style=flat)
[![Docs](https://img.shields.io/badge/docs-online-blue?style=flat)](https://github.com/mvp-zplace/finance-ops-scripts/wiki)
![Issues](https://img.shields.io/badge/issues-private-lightgrey?style=flat)
![Pull Requests](https://img.shields.io/badge/PRs-private-lightgrey?style=flat)

# Finance Ops Scripts
Utilities and documentation for finance, treasury, and accounting workflows (D365, Ramp, Workday Adaptive, FloQast).

## Current Status

Repo initialized — ready for first automation scripts.

## 📦 Installation
### From TestPyPi (for testing builds)
```bash
python -m venv venv
source venv/bin activate  # or venv\Scripts\activate on Windows

pip install --index-url https://test.pypi.org/simple/ --no-deps finance-ops-scripts==0.2.0
```
>**Note**: The `--no-deps` flag is used because dependencies are not hosted on TestPyPi in this build. Remove it when installing from the real PyPi.

---

## 🚀 CLI Usage
Once installed, the package exposes the `ramp-map` CLI entrypoint:
``` bash
ramp-map INPUT.csv OUTPUT.csv [--map-json mapping.json] [--strict] [--strict-amounts] [--dry-run] [--version|-V]
```
### Common Examples:
Dry-run validation (no file written):
``` bash
ramp-map sample.csv sample_out.csv --dry-run
```
Strict mode with custom mapping:
```bash
Note: missing columns treated as empty (lenient mode): Merchant, Cardholder
Dry run: validation succeeded.
rows: 2
invalid_dates: 0 (strict would fail if --strict)
invalid_amounts: 0 (strict would fail if --strict-amounts)
mapping:
  Date -> txn_date
  Amount -> amount
  Merchant -> vendor
  Cardholder -> employee
sample[1]: 2025-08-13,100.00,,
sample[2]: 2025-08-14,50.00,,
```

---

## 📂 Example Project Layout

The repository is organized for clarity between **source code**, **tests**, and **configuration**:
```
finance-ops-scripts/
├── LICENSE.txt # MIT license
├── README.md # Project documentation
├── pyproject.toml # Build & tool configuration
├── release-please-config.json # Automated release config
├── scripts/
│ └── python/
│ ├── init.py
│ └── ramp_export_mapper.py # Main CLI + logic
├── tests/
│ ├── test_cli_dry_run.py
│ ├── test_dry_run_summary.py
│ ├── test_mapper_headers.py
│ ├── test_mapper_strict_and_json.py
│ ├── test_parsers.py
│ └── test_wrappers_smoke.py
└── .github/
└── workflows/
├── ci.yml # Lint/test/build workflow
└── smoke-test.yml # Quick run validation
```

### Key Points
- **scripts/python/** → All Python source code for packaging and CLI.
- **tests/** → Unit and integration tests (`pytest`-based).
- **pyproject.toml** → Defines dependencies, entry points, and tooling config (Ruff, Black, pytest, mypy).
- **release-please-config.json** → Used by Release Please to automate version bumps and changelog generation.
- **.github/workflows/** → GitHub Actions CI/CD pipelines.

> When published to PyPI, only the source package (`scripts/python/`) and necessary metadata files are included.

---

## 📦 Distribution Artifacts

When building for PyPI (`python -m build`), two artifacts are generated in the `dist/` folder:

1. **Source distribution (`.tar.gz`)**
   - Full source code
   - `LICENSE.txt`, `README.md`, `pyproject.toml`, and all package files
   - Useful for inspecting raw source

2. **Wheel (`.whl`)**
   - Pre-built package ready for installation
   - Contains only necessary runtime files:
     ```
     finance_ops_scripts-<version>.dist-info/   # Metadata
     scripts/python/__init__.py
     scripts/python/ramp_export_mapper.py
     ```
   - CLI entry point `ramp-map` is auto-generated via `pyproject.toml` `[project.scripts]` section.

> Both artifacts are uploaded to TestPyPI for validation before going to the real PyPI index.

---

## How CI Works

This repository uses **GitHub Actions** for continuous integration (CI).
The main workflow (`.github/workflows/ci.yml`) runs automatically on:

- Pushes to `main`
- Pull requests targeting `main`
- Manual runs from the Actions tab

### What Runs
1. **Linting**
   - **Ruff** → Python style and lint checks
   - **Black** → Code formatting check (non-auto-fix)
2. **Testing**
   - **Pytest** with coverage (`pytest-cov`)
   - Coverage reports in terminal, XML, and HTML formats
3. **Security**
   - **Bandit** → Python security scan (non-blocking by default)
4. **Coverage Upload**
   - **Codecov** → Uploads `coverage.xml` for tracking branch coverage over time

### Where Coverage Lives
- **Codecov Dashboard:** [View Coverage Reports](https://app.codecov.io/github/mvp-zplace/finance-ops-scripts)
- **Local Output:** `coverage.xml` + `htmlcov/` directory after test runs

### Required Checks
- All CI jobs must pass before merging to `main`
- Direct pushes to `main` are blocked
- Branches are auto-deleted after merge

---

## Issue & PR Templates

This repository includes pre-built templates to standardize contributions and operational tracking.

### Pull Request Template
When opening a PR, a description form will auto-fill with sections for:
- **Summary** – what's changing and why
- **Scope of Change** – areas, systems, backward compatibility
- **Controls & Risk** – control impact, rollback plan
- **Data Sensitivity** – data type, secrets handling
- **Testing** – steps, edge cases
- **Deployment / Runbook** – relevant commands, automation notes

Use this to ensure all changes are well-documented, tested, and safe to merge.

### Issue Templates
When opening a new issue, choose from:

1. **Bug report**
   For defects or unexpected behavior in scripts, docs, or workflows.
   Includes prompts for repro steps, impact, data/systems involved, and acceptance criteria.

2. **Feature request**
   For proposing new functionality or enhancements.
   Includes fields for proposal, scope, controls, and acceptance criteria.

3. **Task / Checklist**
   For recurring operational processes or runbooks (e.g., month-end close, reconciliations).
   Includes pre-checks, step-by-step actions, and post-checks for verification.

---

**Tip:** Keep sensitive data out of all issues and PRs – use `.env` files locally and scrub any attached files before uploading.

## Quick Demo
### Python
Run mapping:
```bash
python scripts/python/ramp_export_mapper.py data/ramp_sample.csv output/ramp_mapped.csv
```
Output:
```bash
Output file: output/ramp_mapped.csv
# CI confirmation run 2025-08-09T03:07:41Z
```

### PowerShell
Run mapping:
```bash
powershell -ExecutionPolicy Bypass -File ./tools/ramp.ps1 -Raw data/ramp_raw.csv -Out output/ramp_mapped.csv
```
Dry-run validation (no files written):
```bash
powershell -ExecutionPolicy Bypass -File ./tools/ramp.ps1 -Raw data/ramp_raw.csv -Out output/ramp_mapped.csv -DryRun
```
**What Happens on Run**

- Validates the CSV
- Writes mapped output to `output/ramp_mapped.csv`
- Archives raw + mapped files in `archive/YYYY-MM-DD/`
- UTF-8 encoding enforced for consistent output

---

## Version
```bash
ramp-map --version
```

## 🤝 How to Contribute

We welcome improvements to scripts, docs, and workflows. Before submitting a PR:

1. **Set up pre-commit**
   Install hooks to ensure linting, formatting, and EOF/line ending rules run locally:

   ```bash
   pip install pre-commit
   pre-commit install
   ```

2. **Run all checks**

   ```bash
   pre-commit run --all-files
   pytest
   ```

3. **Follow commit conventions**
   - Use `chore:`, `feat:`, `fix:`, etc. in commit messages.
   - Keep commits focused; avoid unrelated changes.

4. **Submit a Pull Request**
   PRs auto-fill with a template for summary, scope, controls, and testing. Complete all sections before submission.

> **Note:** Keep sensitive data out of commits. Use `.env` for local secrets.

<!-- `.env` is ignored in `.gitignore` for API tokens or sensitive CI warmup: do not remove -->
<- files were modified by this labeler smoke -->

<!-- release-please: trigger 2025-08-14T20:42:12Z -->
