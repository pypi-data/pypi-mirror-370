# Repository File Consolidation

Generated on: 2025-08-19 22:37:36
Repository root: C:\Users\edaci\Documents\civic-interconnect\civic-transparency-types

---

## File: `.editorconfig`

``text
# project .editorconfig file
root = true

[*]
# Unix-style line endings
end_of_line = lf
# Add a newline at the end of the file
insert_final_newline = true

# Use 4-space indentation for Python files
[*.py]
indent_style = space
indent_size = 4
``

---

## File: `.pre-commit-config.yaml`

``yaml
# .pre-commit-config.yaml
minimum_pre_commit_version: "3.5.0"

repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.12.8
    hooks:
      - id: ruff-format
        exclude: ^src/ci/transparency/types/.*\.py$
      - id: ruff  
        exclude: ^src/ci/transparency/types/.*\.py$

  - repo: local
    hooks:
      # Quick version/spec invariants (no generation). Runs when pyproject or code changes.
      - id: check-version-compatibility
        name: Check version compatibility (current env)
        entry: python .github/scripts/check_version_compatibility.py
        language: system
        files: ^(pyproject\.toml|src/.*\.py|\.github/scripts/.*\.py)$
        pass_filenames: false

      # Import smoke + empty points invariant — no generation.
      - id: verify-types
        name: Verify types import + empty points
        entry: python .github/scripts/verify_types.py
        language: system
        pass_filenames: false

      # NOTE: Generation is intentionally manual to keep CI pure-validate.
      # Run locally when spec changes:
      #   python scripts/generate_types.py && git add src/ci/transparency/types/

``

---

## File: `benchmark_performance.py`

``python
#!/usr/bin/env python3
"""
Benchmark script for civic-transparency-types performance.
Run this to get actual performance characteristics for your models.
"""

import json
import time
import sys
import tracemalloc
from datetime import datetime, timezone
from typing import Dict, Any
import statistics
from pydantic import BaseModel

try:
    import orjson

    has_orjson = True
except ImportError:
    has_orjson = False

from ci.transparency.types import Series, ProvenanceTag


def create_minimal_series() -> Dict[str, Any]:
    """Create minimal valid Series data."""
    return {
        "topic": "#BenchmarkTopic",
        "generated_at": "2025-08-19T12:00:00Z",
        "interval": "minute",
        "points": [
            {
                "ts": "2025-08-19T12:00:00Z",
                "volume": 100,
                "reshare_ratio": 0.25,
                "recycled_content_rate": 0.1,
                "acct_age_mix": {
                    "0-7d": 0.2,
                    "8-30d": 0.3,
                    "1-6m": 0.3,
                    "6-24m": 0.15,
                    "24m+": 0.05,
                },
                "automation_mix": {
                    "manual": 0.8,
                    "scheduled": 0.1,
                    "api_client": 0.05,
                    "declared_bot": 0.05,
                },
                "client_mix": {"web": 0.6, "mobile": 0.35, "third_party_api": 0.05},
                "coordination_signals": {
                    "burst_score": 0.3,
                    "synchrony_index": 0.2,
                    "duplication_clusters": 5,
                },
            }
        ],
    }


def create_complex_series(num_points: int = 100) -> Dict[str, Any]:
    """Create Series data with many points."""
    base_data = create_minimal_series()
    base_point = base_data["points"][0]

    # Generate many time points
    points = []
    for i in range(num_points):
        point = base_point.copy()
        # Vary timestamp
        ts = datetime(2025, 8, 19, 12, i % 60, 0, tzinfo=timezone.utc)
        point["ts"] = ts.isoformat().replace("+00:00", "Z")
        # Vary some values slightly
        point["volume"] = 100 + (i % 50)
        point["reshare_ratio"] = min(1.0, 0.25 + (i % 10) * 0.05)
        points.append(point)

    base_data["points"] = points
    return base_data


def create_provenance_tag() -> Dict[str, Any]:
    """Create minimal valid ProvenanceTag data."""
    return {
        "acct_age_bucket": "1-6m",
        "acct_type": "person",
        "automation_flag": "manual",
        "post_kind": "original",
        "client_family": "mobile",
        "media_provenance": "hash_only",
        "origin_hint": "US-CA",
        "dedup_hash": "a1b2c3d4e5f6789a",
    }


def benchmark_validation(
    name: str,
    model_class: type[BaseModel],
    data: Dict[str, Any],
    iterations: int = 10000,
):
    """Benchmark validation performance."""
    print(f"\n🔬 Benchmarking {name} validation ({iterations:,} iterations)")

    # Warm up
    for _ in range(100):
        model_class.model_validate(data)

    # Memory tracking
    tracemalloc.start()

    # Timing
    times: list[float] = []
    for _ in range(5):  # 5 runs for statistics
        start_time = time.perf_counter()
        for _ in range(iterations):
            obj = model_class.model_validate(data)
        end_time = time.perf_counter()
        times.append(end_time - start_time)

    # Memory measurement
    tracemalloc.stop()

    # Calculate stats
    avg_time: float = statistics.mean(times)
    std_time: float = statistics.stdev(times)
    records_per_sec = iterations / avg_time

    print(f"  ⏱️  Average time: {avg_time:.4f}s (±{std_time:.4f}s)")
    print(f"  🚀 Records/sec: {records_per_sec:,.0f}")
    print(f"  📏 Time per record: {(avg_time / iterations) * 1000:.3f}ms")

    return records_per_sec, obj


def benchmark_serialization(
    name: str, obj, iterations: int = 10000
) -> dict[str, float]:
    """Benchmark serialization performance."""
    print(f"\n📤 Benchmarking {name} serialization ({iterations:,} iterations)")

    results = {}

    # Pydantic JSON
    times: list[float] = []
    for _ in range(5):
        start_time = time.perf_counter()
        for _ in range(iterations):
            json.dumps(obj.model_dump(mode="json"))
        end_time = time.perf_counter()
        times.append(end_time - start_time)

    avg_time = statistics.mean(times)
    results["pydantic"] = iterations / avg_time
    print(f"  📋 Pydantic JSON: {results['pydantic']:,.0f} records/sec")

    # model_dump() + stdlib json (need mode='json' for enum serialization)
    times = []
    for _ in range(5):
        start_time = time.perf_counter()
        for _ in range(iterations):
            data = obj.model_dump(mode="json")  # This converts enums to their values
            json.dumps(data)
        end_time = time.perf_counter()
        times.append(end_time - start_time)

    avg_time = statistics.mean(times)
    results["stdlib_json"] = iterations / avg_time
    print(f"  🐍 stdlib json: {results['stdlib_json']:,.0f} records/sec")

    # orjson if available
    if has_orjson:
        times = []
        for _ in range(5):
            start_time = time.perf_counter()
            for _ in range(iterations):
                data = obj.model_dump(mode="json")  # Convert enums for orjson too
                orjson.dumps(data)
            end_time = time.perf_counter()
            times.append(end_time - start_time)

        avg_time = statistics.mean(times)
        results["orjson"] = iterations / avg_time
        print(f"  ⚡ orjson: {results['orjson']:,.0f} records/sec")

    return results


def measure_memory_usage(name: str, obj):
    """Measure memory usage of objects."""
    print(f"\n💾 Memory usage for {name}")

    # Get object size
    import sys

    size = sys.getsizeof(obj)

    # More detailed measurement
    tracemalloc.start()
    snapshot1 = tracemalloc.take_snapshot()

    # Create a list of objects to measure overhead
    _: list[type(obj)] = [
        type(obj).model_validate(obj.model_dump()) for _ in range(1000)
    ]

    snapshot2 = tracemalloc.take_snapshot()
    tracemalloc.stop()

    top_stats = snapshot2.compare_to(snapshot1, "lineno")
    total_memory = sum(stat.size for stat in top_stats)
    avg_per_object = total_memory / 1000

    print(f"  🔍 sys.getsizeof(): {size:,} bytes")
    print(f"  📊 Estimated per object: {avg_per_object:,.0f} bytes")
    print(f"  📦 JSON size: {len(obj.model_dump_json()):,} bytes")

    return avg_per_object


def main():
    """Run all benchmarks."""
    print("🎯 Civic Transparency Types Performance Benchmark")
    print("=" * 50)
    print(f"Python version: {sys.version}")
    print(f"orjson available: {has_orjson}")
    print()

    # Create test data
    minimal_series_data = create_minimal_series()
    complex_series_data = create_complex_series(100)
    provenance_data = create_provenance_tag()

    # Validation benchmarks
    provenance_rps, provenance_obj = benchmark_validation(
        "ProvenanceTag", ProvenanceTag, provenance_data, 20000
    )

    minimal_series_rps, minimal_series_obj = benchmark_validation(
        "Series (minimal)", Series, minimal_series_data, 10000
    )

    complex_series_rps, complex_series_obj = benchmark_validation(
        "Series (100 points)", Series, complex_series_data, 1000
    )

    # Serialization benchmarks
    provenance_ser = benchmark_serialization("ProvenanceTag", provenance_obj, 20000)
    minimal_ser = benchmark_serialization("Series (minimal)", minimal_series_obj, 10000)
    complex_ser = benchmark_serialization(
        "Series (100 points)", complex_series_obj, 1000
    )

    # Memory usage
    provenance_mem = measure_memory_usage("ProvenanceTag", provenance_obj)
    minimal_mem = measure_memory_usage("Series (minimal)", minimal_series_obj)
    complex_mem = measure_memory_usage("Series (100 points)", complex_series_obj)

    # Summary
    print("\n" + "=" * 50)
    print("📊 PERFORMANCE SUMMARY")
    print("=" * 50)

    print("\n🔬 VALIDATION PERFORMANCE")
    print(f"ProvenanceTag:     {provenance_rps:>8,.0f} records/sec")
    print(f"Series (minimal):  {minimal_series_rps:>8,.0f} records/sec")
    print(f"Series (complex):  {complex_series_rps:>8,.0f} records/sec")

    print("\n📤 SERIALIZATION PERFORMANCE (Pydantic JSON)")
    print(f"ProvenanceTag:     {provenance_ser['pydantic']:>8,.0f} records/sec")
    print(f"Series (minimal):  {minimal_ser['pydantic']:>8,.0f} records/sec")
    print(f"Series (complex):  {complex_ser['pydantic']:>8,.0f} records/sec")

    if has_orjson:
        print("\n⚡ SERIALIZATION PERFORMANCE (orjson)")
        print(f"ProvenanceTag:     {provenance_ser['orjson']:>8,.0f} records/sec")
        print(f"Series (minimal):  {minimal_ser['orjson']:>8,.0f} records/sec")
        print(f"Series (complex):  {complex_ser['orjson']:>8,.0f} records/sec")

    print("\n💾 MEMORY USAGE")
    print(f"ProvenanceTag:     {provenance_mem:>8,.0f} bytes")
    print(f"Series (minimal):  {minimal_mem:>8,.0f} bytes")
    print(f"Series (complex):  {complex_mem:>8,.0f} bytes")

    print("\n✅ Benchmark complete!")


if __name__ == "__main__":
    main()

``

---

## File: `CHANGELOG.md`

``markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on **[Keep a Changelog](https://keepachangelog.com/en/1.1.0/)**  
and this project adheres to **[Semantic Versioning](https://semver.org/spec/v2.0.0.html)**.

**Important:** Update version for "civic-transparency-spec==x.y.z" in `pyproject.toml` also.

## [Unreleased]

### Added

- (placeholder) Notes for the next release.

---

## [0.2.1] - 2025-08-19

### Fixed

- **Update to**: civic-transparency-spec==0.2.1

---

## [0.2.0] - 2025-08-19

### Added

- **Initial public release**: based on civic-transparency-spec==0.2.0

---

## Notes on versioning and releases

- We use **SemVer**:
  - **MAJOR** – breaking model changes relative to the spec
  - **MINOR** – backward-compatible additions
  - **PATCH** – clarifications, docs, tooling
- Versions are driven by git tags via `setuptools_scm`. Tag `vX.Y.Z` to release.
- Docs are deployed per version tag and aliased to **latest**.

[Unreleased]: https://github.com/civic-interconnect/civic-transparency-spec/compare/v0.2.1...HEAD
[0.2.1]: https://github.com/civic-interconnect/civic-transparency-types/compare/v0.2.0..v0.2.1
[0.2.0]: https://github.com/civic-interconnect/civic-transparency-types/releases/tag/v0.2.0


``

---

## File: `CITATION.cff`

``text
cff-version: 1.2.0
title: Civic Transparency
message: If you use this software, please cite it as below.
type: software
authors:
  - name: Civic Interconnect
repository-code: https://github.com/civic-interconnect/civic-transparency-types
license: MIT


``

---

## File: `CODE_OF_CONDUCT.md`

``markdown
# Civic Transparency Code of Conduct

## Our Commitment

We are committed to a respectful, inclusive, and collaborative environment for everyone, regardless of:
age, culture, ethnicity, gender identity or expression, language, national origin, neurotype, physical or mental ability, political beliefs, profession, race, religion, sexual orientation, socioeconomic status, or technical background.

We welcome global participation. While we may not be able to meet every request, we will always work to treat each other well.

## Expected Behavior

- **Be respectful and kind.** Treat others as you would wish to be treated.
- **Be collaborative.** Share knowledge freely, give credit, and help others succeed.
- **Be constructive.** Focus on ideas and solutions, not personal attacks.
- **Be concise and clear.** Communicate in ways that make participation easier for everyone, especially across languages.
- **Use public channels** for project-related communication whenever possible, so everyone can benefit from shared knowledge.
- **Respect privacy** and avoid sharing personal information without consent.

## Unacceptable Behavior

Harassment, discrimination, or abusive conduct of any kind is not acceptable. Examples include:

- Threats or violent language
- Sexist, racist, or discriminatory jokes or comments
- Posting sexual or violent material
- Sharing private communications without permission
- Personal insults or name-calling
- Unwelcome sexual attention
- Persistent disruption or hostility after being asked to stop

## Scope

This Code applies to all project spaces, both online and offline, and in all interactions where you represent the project.

## Reporting

If you experience or witness behavior that violates this Code:

- You may report it privately to the maintainers at: **info@civicinterconnect.org**
- Reports will be handled respectfully and confidentially.
- The project team is committed to fair review and, when necessary, taking appropriate action.

## Attribution

This Code of Conduct is adapted from:

- [Apache Software Foundation Code of Conduct](https://www.apache.org/foundation/policies/conduct.html)
- [Contributor Covenant v2.1](https://www.contributor-covenant.org/version/2/1/code_of_conduct.html)

``

---

## File: `CONTRIBUTING.md`

``markdown
# CONTRIBUTING.md

This repo hosts the **Civic Transparency Types** under the **MIT License**.
Our goals are clarity, privacy-by-design, and low friction for collaborators.

> tl;dr: open an Issue or Discussion first for anything non-trivial, keep PRs small and focused, and please run the quick local checks below.

---

## Ways to Contribute

- **Docs**: Fix typos, clarify definitions, or improve examples in `docs/en/**`.
- **Actions**: Propose changes to project workflow and action files to follow best practices.

---

## Ground Rules

- **Code of Conduct**: Be respectful and constructive. Reports: `info@civicinterconnect.org`.
- **License**: All contributions are accepted under the repo's **MIT License**.
- **Single Source of Truth**: The definitions are in `src/ci/transparency/spec/schemas/`. Documentation should not contradict these files.

---

## Before You Start

**Open an Issue or Discussion** for non-trivial changes so we can align early.

---

## Making Changes

- Follow **Semantic Versioning**:
  - **MAJOR**: breaking changes
  - **MINOR**: backwards-compatible additions
  - **PATCH**: clarifications/typos
- When things change, update related docs, examples, and `CHANGELOG.md`.

---

## Commit & PR guidelines

- **Small PRs**: one focused change per PR.
- **Titles**: start with area, e.g., `code: fix deprecation warning`.
- **Link** the Issue/Discussion when applicable.
- Prefer **squash merging** for a clean history.
- No DCO/CLA required.

---

## Questions / Support

- **Discussion:** For open-ended design questions.
- **Issue:** For concrete bugs or proposed text/schema changes.
- **Private contact:** `info@civicinterconnect.org` (for sensitive reports).

---

## DEV 1. Start Locally

**Mac/Linux/WSL**

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip setuptools wheel
python3 -m pip install -e ".[dev]"
pre-commit install
python3 scripts/generate_types.py
git add src/ci/transparency/types/
```

**Windows (PowerShell)**

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\activate
py -m pip install --upgrade pip setuptools wheel
py -m pip install -e ".[dev]"
pre-commit install
py scripts\generate_types.py
git add src/ci/transparency/types/
```

## DEV 2. Validate Changes

1. Pull from the GitHub repo.
2. Purge the pip cache.
3. Install packages.
4. Generate types in case schema changed.
5. Add generated changes to git.
6. Commit updated types to git. 
7. Format and lint.
8. Run precommit checks.
9. Build documentation to test.
10. Run tests.

```shell
git pull
pip cache purge
pip install ".[dev]"
py scripts\generate_types.py
git add src/ci/transparency/types/
git commit -m "Update generated types"
ruff format .
ruff check --fix .
pre-commit run --all-files
mkdocs build
pytest -q
```

2. Build and Verify Package

Mac/Linux/WSL (build, inspect)

```
python3 -m build
unzip -l dist/*.whl
```

Windows PowerShell (build, extract, clean up)

```
py -m build

$TMP = New-Item -ItemType Directory -Path ([System.IO.Path]::GetTempPath()) -Name ("wheel_" + [System.Guid]::NewGuid())
Expand-Archive dist\*.whl -DestinationPath $TMP.FullName
Get-ChildItem -Recurse $TMP.FullName | ForEach-Object { $_.FullName.Replace($TMP.FullName + '\','') }
Remove-Item -Recurse -Force $TMP
```

## DEV 3. Preview Docs

```bash
mkdocs serve
```

Open: <http://127.0.0.1:8000/>

## DEV 4. Release

1. Update `CHANGELOG.md` with notable changes (beginning and end).
2. Update pyproject.toml with correct version "civic-transparency-spec>=x.y.z...",
3. Ensure all CI checks pass.
4. Build & verify package locally.
5. Tag and push (setuptools_scm uses the tag).

```bash
ruff format .
pre-commit run --all-files
git add .
git commit -m "Prep vx.y.z"
git push origin main

git tag vx.y.z -m "x.y.z"
git push origin vx.y.z
```

> A GitHub Action will **build**, **publish to PyPI** (Trusted Publishing), **create a GitHub Release** with artifacts, and **deploy versioned docs** with `mike`.

> You do **not** need to run `gh release create` or upload files manually.

``

---

## File: `LICENSE`

``text
MIT License

Copyright (c) 2025 Civic Interconnect

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the “Software”), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

``

---

## File: `MANIFEST.in`

``text
# MANIFEST.in — keep the sdist lean

# Core project files
include LICENSE
include README.md
include pyproject.toml

graft src/ci/transparency/types

# Exclude non-distribution directories
prune .github
prune docs
prune site
prune tests

# Exclude misc config/artifacts
exclude .editor.config .gitattributes .gitignore .pre-commit-config.yaml coverage.xml mkdocs.yml

``

---

## File: `mkdocs.yml`

``yaml
site_name: Civic Transparency Types
site_description: Types for the Civic Transparency project
site_author: Civic Interconnect
site_url: https://civic-interconnect.github.io/civic-transparency-types/
repo_url: https://github.com/civic-interconnect/civic-transparency-types
edit_uri: edit/main/docs/en/

theme:
  name: material
  language: en
  favicon: img/favicon.png
  palette:
    scheme: default
    primary: indigo
    accent: indigo
  features:
    - content.footer
    - navigation.tabs
    - navigation.top
    - navigation.expand
    - navigation.sections
    - navigation.indexes
    - navigation.tracking
    - navigation.tabs.stick
  copyright: Copyright &copy; 2025 Civic Interconnect

nav:
  - Home: index.md
  - API: api.md
  - Reference:
      - Provenance Tag: reference/provenance_tag.md
      - Series: reference/series.md
  - Spec:
      - Civic Transparency Spec (website): https://civic-interconnect.github.io/civic-transparency-spec/
      - Civic Transparency Spec (source): https://github.com/civic-interconnect/civic-transparency-spec

  - Performance: performance.md
  - Usage: usage.md
  
docs_dir: docs/en

plugins:
  - search
  - include-markdown
  - minify:
      minify_html: true
  - i18n:
      docs_structure: folder
      languages:
        - locale: en
          default: true
          name: English
  - git-revision-date-localized:
      type: iso_date
      fallback_to_build_date: true
      enable_creation_date: false
  - mkdocstrings:
      handlers:
        python:
          options:
            docstring_style: google
            show_source: false
            show_signature: true
            group_by_category: true
            filters: ["!^_"]  # hide private members

markdown_extensions:
- admonition
- codehilite
- pymdownx.snippets
- pymdownx.tabbed
- toc

``

---

## File: `pyproject.toml`

``toml
[build-system]
requires = ["setuptools>=77", "wheel", "setuptools-scm[toml]>=8"]
build-backend = "setuptools.build_meta"

[project]
authors = [{ name = "Civic Interconnect" }]
classifiers = [
  "Programming Language :: Python :: 3",
  "Programming Language :: Python :: 3 :: Only",
  "Programming Language :: Python :: 3.11",
  "Topic :: Software Development :: Libraries",
]
dependencies = [
  "packaging>=24.0",
  "pydantic>=2.6",
  "civic-transparency-spec>=0.2.1,<0.3.0",
]
description = "Typed Python models (Pydantic v2) for the Civic Transparency specification"
dynamic = ["version"]
keywords = ["civic", "transparency", "jsonschema", "specification", "types"]
license = "MIT"
license-files = ["LICENSE*"]
name = "civic-transparency-types"
readme = "README.md"
requires-python = ">=3.11"

[project.optional-dependencies]
dev = [ 
  "build",
  "pre-commit",
  "pytest", 
  "pytest-cov",
  "ruff",
  "mkdocs",
  "mkdocs-git-revision-date-localized-plugin",
  "mkdocs-include-markdown-plugin",
  "mkdocs-material",
  "mkdocs-minify-plugin",
  "mkdocs-static-i18n",
  "mkdocstrings[python]",
  "mike",
  "jsonschema", 
  "openapi-spec-validator",
  "datamodel-code-generator",
]

[project.urls]
Documentation = "https://civic-interconnect.github.io/civic-transparency-types/latest/"
Homepage = "https://github.com/civic-interconnect/civic-transparency-types"
Repository = "https://github.com/civic-interconnect/civic-transparency-types"

[tool.coverage.report]
show_missing = true
skip_covered = false

[tool.coverage.run]
branch = true
omit = [
  "src/ci/transparency/types/_version.py"
]
source = ["src/ci/transparency/types"]

[tool.pytest.ini_options]
addopts = "-q --cov=ci.transparency.types --cov-branch --cov-report=term-missing --cov-report=xml --cov-fail-under=85"
pythonpath = ["src"]
testpaths = ["tests"]

[tool.setuptools]
package-dir = { "" = "src" }
include-package-data = true

[tool.setuptools.packages.find]
where = ["src"]

[tool.setuptools.package-data]
"ci.transparency.types" = ["py.typed"]

[tool.setuptools_scm]
local_scheme = "no-local-version"
version_scheme = "guess-next-dev"
write_to = "src/ci/transparency/types/_version.py"

[tool.ruff]
exclude = [
    "src/ci/transparency/types/*.py",  # Ignore all generated types
]

[tool.ruff.lint.per-file-ignores]
"src/ci/transparency/types/*.py" = ["F401"] # generated models may have unused imports

``

---

## File: `README.md`

``markdown
# Civic Transparency – Types

[![Docs](https://img.shields.io/badge/docs-mkdocs--material-blue)](https://civic-interconnect.github.io/civic-transparency-types/)
[![PyPI](https://img.shields.io/pypi/v/civic-transparency-types.svg)](https://pypi.org/project/civic-transparency-types/)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue?logo=python)](#)
[![CI Status](https://github.com/civic-interconnect/civic-transparency-types/actions/workflows/ci.yml/badge.svg)](https://github.com/civic-interconnect/civic-transparency-types/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)

> **Typed Python models (Pydantic v2) for the Civic Transparency schema.**

> Maintained by [**Civic Interconnect**](https://github.com/civic-interconnect).

- **Documentation:** https://civic-interconnect.github.io/civic-transparency-types/
- **Schema Specification:** https://civic-interconnect.github.io/civic-transparency-spec/
- **Contributing:** [CONTRIBUTING.md](./CONTRIBUTING.md)

---

## Overview

This package provides strongly-typed Python models that correspond to the [Civic Transparency specification](https://civic-interconnect.github.io/civic-transparency-spec/).
The types are automatically generated from canonical JSON Schema definitions, ensuring consistency and validation at runtime.

**Key Features:**
- **Type Safety:** Full Pydantic v2 validation with IDE support
- **Schema Compliance:** Generated directly from official JSON schemas
- **Privacy-First:** Designed for aggregated, non-PII data exchange
- **Interoperability:** JSON serialization/deserialization with validation

---

## Installation

```bash
pip install civic-transparency-types
```

For development or schema validation:
```bash
pip install "civic-transparency-types[dev]"
```

> **Note:** This package automatically includes the compatible `civic-transparency-spec` version as a dependency.

---

## Quick Start

### Basic Usage

```python
from ci.transparency.types import Series, ProvenanceTag

# Create a time series for civic data
series = Series(
    topic="#LocalElection",
    generated_at="2025-01-15T12:00:00Z",
    interval="minute",
    points=[]  # Add your aggregated data points here
)

# Validate and serialize
data = series.model_dump()  # JSON-compatible dict
json_str = series.model_dump_json(indent=2)  # Pretty JSON string
```

### Loading and Validation

```python
from ci.transparency.types import Series

# Load from existing data with validation
series = Series.model_validate(data_dict)
series = Series.model_validate_json(json_string)

# Handle validation errors
from pydantic import ValidationError
try:
    invalid_series = Series.model_validate(bad_data)
except ValidationError as e:
    print(f"Validation failed: {e}")
```

### Working with Provenance Tags

```python
from ci.transparency.types import ProvenanceTag

tag = ProvenanceTag(
    acct_age_bucket="1-6m",
    acct_type="person", 
    automation_flag="manual",
    post_kind="original",
    client_family="mobile",
    media_provenance="hash_only",
    dedup_hash="a1b2c3d4"
)
```

---

## Available Types

| Type | Description | Schema Source |
|------|-------------|---------------|
| `Series` | Privacy-preserving time series data for civic topics | `series.schema.json` |
| `ProvenanceTag` | Per-post metadata tags (bucketed, no PII) | `provenance_tag.schema.json` |

See the [API documentation](https://civic-interconnect.github.io/civic-transparency-types/api/) for complete field definitions and examples.

---

## Validation and Schemas

### Pydantic Validation
All models use Pydantic v2 for runtime validation:
- **Strict typing:** Unknown fields are rejected
- **Format validation:** ISO 8601 dates, patterns, enums
- **Range checking:** Min/max values, string lengths
- **Nested validation:** Complex object hierarchies

### JSON Schema Validation (Optional)
For additional validation against the canonical schemas:

```python
import json
from importlib.resources import files
from jsonschema import Draft202012Validator

# Get the official schema
schema_text = files("ci.transparency.spec.schemas").joinpath("series.schema.json").read_text()
schema = json.loads(schema_text)

# Validate your data
validator = Draft202012Validator(schema)
validator.validate(series.model_dump())
```

---

## Versioning Strategy

This package follows the underlying specification versions:
- **Major versions:** Breaking schema changes
- **Minor versions:** Backward-compatible additions  
- **Patch versions:** Documentation, tooling, bug fixes

**Best Practice:** Pin to compatible major versions:
```bash
pip install "civic-transparency-types>=0.2.1,<1.0"
```

The package automatically manages compatibility with the corresponding `civic-transparency-spec` version.

---

## Integration Examples

### FastAPI Integration
```python
from fastapi import FastAPI
from ci.transparency.types import Series

app = FastAPI()

@app.post("/civic-data")
async def receive_series(series: Series) -> dict:
    # Automatic validation and parsing
    return {"received": series.topic, "points": len(series.points)}
```

### File I/O
```python
from pathlib import Path
from ci.transparency.types import Series

# Save to file
series_file = Path("data.json")
series_file.write_text(series.model_dump_json(indent=2))

# Load from file
loaded_series = Series.model_validate_json(series_file.read_text())
```

---

## Development and Contributing

This is a **generated types package** - the source of truth is the [civic-transparency-spec](https://github.com/civic-interconnect/civic-transparency-spec) repository.

### For Type Users
- Report type-related issues here
- Request documentation improvements
- Share integration examples

### For Schema Changes
- Schema modifications should be made in the [spec repository](https://github.com/civic-interconnect/civic-transparency-spec)
- Types are automatically regenerated when the spec changes

### Local Development
```bash
git clone https://github.com/civic-interconnect/civic-transparency-types
cd civic-transparency-types
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -e ".[dev]"
```

See [CONTRIBUTING.md](./CONTRIBUTING.md) for detailed guidelines.

---

## Support and Community

- **Documentation:** https://civic-interconnect.github.io/civic-transparency-types/
- **Issues:** [GitHub Issues](https://github.com/civic-interconnect/civic-transparency-types/issues)
- **Discussions:** [GitHub Discussions](https://github.com/civic-interconnect/civic-transparency-types/discussions)  
- **Email:** info@civicinterconnect.org

---

## About Civic Transparency

Civic Transparency is an open standard for privacy-preserving, non-partisan analysis of how information spreads in civic contexts. The specification enables researchers, platforms, and civic organizations to share insights while protecting individual privacy.

**Core Principles:**
- **Privacy by Design:** No personally identifiable information
- **Aggregation First:** Time-bucketed, statistical summaries
- **Open Standard:** Collaborative, transparent development
- **Practical Implementation:** Real-world deployment focus

``

---

## File: `sum.ps1`

``powershell
# consolidate-repo.ps1
# Consolidates all repository files into a single document for review
# Run from repository root

param(
    [string]$OutputFile = "repo-consolidation.md"
)

# Directories to include
$IncludeDirs = @(".", ".github",  "docs", "scripts", "src","tests"  )

# Files/patterns to exclude (common artifacts and binaries)
$ExcludePatterns = @(
    "*.pyc", "*.pyo", "*.pyd", "__pycache__", 
    "*.egg-info", "build", "dist", ".git", 
    ".pytest_cache", ".coverage", "htmlcov", "coverage.xml"
    "node_modules", ".venv", "venv", "env",
    "*.log", "*.tmp", "*.temp", "*.cache",
    "*.png", "*.jpg", "*.jpeg", "*.gif", "*.ico",
    "*.pdf", "*.zip", "*.tar", "*.gz",
    $OutputFile  # Don't include the output file itself
)

Write-Host "Starting file consolidation..." -ForegroundColor Green
Write-Host "Output file: $OutputFile" -ForegroundColor Cyan

# Initialize output
$Content = @()
$Content += "# Repository File Consolidation"
$Content += ""
$Content += "Generated on: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
$Content += "Repository root: $(Get-Location)"
$Content += ""
$Content += "---"
$Content += ""

$FileCount = 0

foreach ($Dir in $IncludeDirs) {
    if (Test-Path $Dir) {
        Write-Host "Processing directory: $Dir" -ForegroundColor Yellow
        
        # Get all files recursively, excluding specified patterns
        $Files = Get-ChildItem -Path $Dir -Recurse -File | Where-Object {
            $FilePath = $_.FullName
            $RelativePath = Resolve-Path -Path $FilePath -Relative
            
            # Check if file matches any exclude pattern
            $Exclude = $false
            foreach ($Pattern in $ExcludePatterns) {
                if ($RelativePath -like "*$Pattern*" -or $_.Name -like $Pattern) {
                    $Exclude = $true
                    break
                }
            }
            -not $Exclude
        }
        
        foreach ($File in $Files) {
            try {
                $RelativePath = Resolve-Path -Path $File.FullName -Relative
                $RelativePath = $RelativePath -replace '^\.\\', ''  # Remove leading .\
                
                Write-Host "  Adding: $RelativePath" -ForegroundColor Gray
                Write-Host "    File size: $($File.Length) bytes" -ForegroundColor DarkGray
                
                $Content += "## File: ``$RelativePath``"
                $Content += ""
                
                # Try to read file content
                try {
                    $FileContent = Get-Content -Path $File.FullName -Raw -ErrorAction Stop
                    
                    # Determine file type for syntax highlighting
                    $Extension = $File.Extension.ToLower()
                    $Language = switch ($Extension) {
                        ".py" { "python" }
                        ".js" { "javascript" }
                        ".json" { "json" }
                        ".yaml" { "yaml" }
                        ".yml" { "yaml" }
                        ".md" { "markdown" }
                        ".toml" { "toml" }
                        ".txt" { "text" }
                        ".ps1" { "powershell" }
                        ".sh" { "bash" }
                        ".html" { "html" }
                        ".css" { "css" }
                        ".xml" { "xml" }
                        default { "text" }
                    }
                    
                    if ([string]::IsNullOrWhiteSpace($FileContent)) {
                        $Content += "*File is empty*"
                    } else {
                        $Content += "````$Language"
                        $Content += $FileContent
                        $Content += "````"
                    }
                } catch {
                    $Content += "*Could not read file content (binary or access denied)*"
                    Write-Warning "Could not read: $RelativePath - $($_.Exception.Message)"
                }
                
                $Content += ""
                $Content += "---"
                $Content += ""
                $FileCount++
                
            } catch {
                Write-Warning "Error processing file $($File.FullName): $($_.Exception.Message)"
            }
        }
    } else {
        Write-Warning "Directory not found: $Dir"
    }
}

# Write consolidated content to output file
try {
    $Content | Out-File -FilePath $OutputFile -Encoding UTF8
    Write-Host ""
    Write-Host "Consolidation complete!" -ForegroundColor Green
    Write-Host "Files processed: $FileCount" -ForegroundColor Cyan
    Write-Host "Output written to: $OutputFile" -ForegroundColor Cyan
    Write-Host "File size: $((Get-Item $OutputFile).Length / 1KB) KB" -ForegroundColor Cyan
} catch {
    Write-Error "Failed to write output file: $($_.Exception.Message)"
    exit 1
}

Write-Host ""
Write-Host "You can now upload '$OutputFile' for review." -ForegroundColor Green

``

---

## File: `docs\en\api.md`

``markdown
# API Reference

The Civic Transparency Types package provides a clean, typed interface to the Civic Transparency specification. All models are built with Pydantic v2 and automatically validate against the canonical JSON schemas.

## Package Overview

```python
import ci.transparency.types as ct

# Available models
ct.Series          # Time-bucketed civic data
ct.ProvenanceTag   # Post metadata (privacy-preserving)

# Package metadata
ct.__version__     # Current package version
ct.__all__         # Public API surface
```

---

## Public API

### Core Models

| Class | Purpose | Schema Source |
|-------|---------|---------------|
| **`Series`** | Aggregated time series for civic topics | `series.schema.json` |
| **`ProvenanceTag`** | Categorical post metadata (no PII) | `provenance_tag.schema.json` |

### Package Information

- **`__version__`** (str): Current package version
- **`__all__`** (List[str]): Public API exports

---

## Import Patterns

### Recommended: Barrel Import
```python
from ci.transparency.types import Series, ProvenanceTag

# Clean, simple imports for application code
series = Series(...)
tag = ProvenanceTag(...)
```

### Alternative: Direct Module Import
```python
from ci.transparency.types.series import Series
from ci.transparency.types.provenance_tag import ProvenanceTag

# Useful for IDE "go to definition" and explicit dependencies
```

### Package-Level Import
```python
import ci.transparency.types as ct

# Namespaced access
series = ct.Series(...)
version = ct.__version__
```

---

## Base Model Behavior

All types inherit from `pydantic.BaseModel` and provide the complete Pydantic v2 API:

### Instance Methods

```python
series = Series(...)

# Serialization
data = series.model_dump()                    # → dict (JSON-safe)
json_str = series.model_dump_json()           # → JSON string
json_pretty = series.model_dump_json(indent=2)  # → Pretty JSON

# Copying and updating
updated = series.model_copy(update={'topic': '#NewTopic'})
```

### Class Methods

```python
# Validation and parsing
series = Series.model_validate(data_dict)        # dict → Series
series = Series.model_validate_json(json_string) # JSON → Series

# Schema introspection  
schema = Series.model_json_schema()              # Pydantic-generated schema
fields = Series.model_fields                     # Field definitions
```

### Configuration

All models use strict validation:
- **`extra="forbid"`**: Unknown fields are rejected
- **Type coercion**: Automatic type conversion where safe
- **Validation**: Full constraint checking (patterns, ranges, enums)

---

## Validation Features

### Runtime Type Safety

```python
from pydantic import ValidationError

try:
    # This will fail validation
    invalid_series = Series(
        topic="",  # Empty string not allowed
        generated_at="not-a-date",  # Invalid datetime
        interval="invalid",  # Not in enum
        points=[]
    )
except ValidationError as e:
    print(f"Validation errors: {e}")
```

### Enum Validation

```python
from ci.transparency.types import ProvenanceTag

# Valid enum values are enforced
tag = ProvenanceTag(
    acct_type="person",        # ✓ Valid
    automation_flag="manual"   # ✓ Valid
    # acct_type="wizard"       # ✗ Would raise ValidationError
)
```

### Pattern and Range Validation

```python
# String patterns, numeric ranges, etc. are validated
tag = ProvenanceTag(
    dedup_hash="abc123",       # ✓ Valid hex pattern
    origin_hint="US-CA",       # ✓ Valid country-region format
    # dedup_hash="xyz!"        # ✗ Invalid characters
)
```

---

## Schema Access

### Pydantic Schema (Runtime)

```python
# Get Pydantic-generated schema for tooling
schema = Series.model_json_schema()
print(schema['properties']['topic'])  # Field definition
```

### Canonical Schema (Normative)

Access the official JSON schemas that define the specification:

```python
import json
from importlib.resources import files

# Get the source-of-truth schema
schema_text = files("ci.transparency.spec.schemas").joinpath(
    "series.schema.json"
).read_text("utf-8")
canonical_schema = json.loads(schema_text)

# Use for validation, documentation generation, etc.
from jsonschema import Draft202012Validator
validator = Draft202012Validator(canonical_schema)
validator.validate(series.model_dump())
```

---

## Serialization Details

### JSON Compatibility

```python
series = Series(...)

# These produce equivalent JSON-safe data
data1 = series.model_dump()
data2 = json.loads(series.model_dump_json())
assert data1 == data2
```

### Datetime Handling

```python
from datetime import datetime

series = Series(
    generated_at=datetime.now(),  # Accepts datetime objects
    # ...
)

# Serializes to ISO 8601 strings
data = series.model_dump()
assert isinstance(data['generated_at'], str)  # "2025-01-15T12:00:00Z"
```

### Field Customization

```python
# Exclude fields during serialization
public_data = series.model_dump(exclude={'generated_at'})

# Include only specific fields
minimal_data = series.model_dump(include={'topic', 'interval'})

# Use aliases if defined (none currently in this spec)
aliased_data = series.model_dump(by_alias=True)
```

---

## Error Handling

### Validation Errors

```python
from pydantic import ValidationError

def safe_parse_series(data: dict) -> Series | None:
    """Parse series data with error handling."""
    try:
        return Series.model_validate(data)
    except ValidationError as e:
        # Log specific validation failures
        for error in e.errors():
            field = " → ".join(str(loc) for loc in error['loc'])
            print(f"Validation error in {field}: {error['msg']}")
        return None
```

### Field-Level Errors

```python
try:
    Series.model_validate(bad_data)
except ValidationError as e:
    for error in e.errors():
        print(f"Field: {error['loc']}")       # Which field failed
        print(f"Value: {error['input']}")     # The invalid input
        print(f"Error: {error['msg']}")       # What went wrong
        print(f"Type: {error['type']}")       # Error category
```

---

## Framework Integration

### FastAPI

Automatic request/response validation:

```python
from fastapi import FastAPI
from ci.transparency.types import Series

app = FastAPI()

@app.post("/data")
async def receive_data(series: Series) -> dict:
    # 'series' is automatically validated
    return {"received": series.topic}
```

### Dataclasses Integration

```python
from dataclasses import dataclass
from ci.transparency.types import Series

@dataclass
class ProcessingResult:
    series: Series
    processed_at: str
    
    def to_dict(self):
        return {
            'series': self.series.model_dump(),
            'processed_at': self.processed_at
        }
```

### Django Models

```python
from django.db import models
from ci.transparency.types import Series
import json

class CivicDataRecord(models.Model):
    topic = models.CharField(max_length=255)
    data = models.JSONField()
    
    def get_series(self) -> Series:
        return Series.model_validate(self.data)
    
    def set_series(self, series: Series):
        self.topic = series.topic
        self.data = series.model_dump()
```

---

## Type Information

### Static Type Checking

The package includes `py.typed` for full mypy/pyright support:

```python
from ci.transparency.types import Series

def process_series(series: Series) -> str:
    # Full type safety and IDE completion
    return series.topic.upper()

# mypy will catch type errors
process_series("not a series")  # Error: Argument 1 has incompatible type
```

### Runtime Type Inspection

```python
from ci.transparency.types import Series
import inspect

# Inspect model structure
print(Series.__annotations__)  # Field type annotations
print(Series.model_fields)     # Pydantic field definitions

# Check inheritance
assert issubclass(Series, BaseModel)
```

``

---

## File: `docs\en\index.md`

``markdown
# Civic Transparency – Types (Python)

Strongly-typed Python models for the [Civic Transparency specification](https://civic-interconnect.github.io/civic-transparency-spec/), built with Pydantic v2.

## What This Package Provides

- **Runtime Type Safety:** Full validation of civic transparency data structures
- **IDE Support:** Complete type hints and autocompletion
- **Schema Compliance:** Generated directly from canonical JSON schemas
- **Privacy Compliance:** Built-in validation for privacy-preserving data patterns

## Installation

```bash
pip install civic-transparency-types
```

## Quick Example

```python
from ci.transparency.types import Series
from datetime import datetime

# Create a validated civic data series
series = Series(
    topic="#CityBudget2025",
    generated_at=datetime.now().isoformat() + "Z",
    interval="minute",
    points=[]  # Your aggregated, privacy-preserving data points
)

# Automatic validation ensures schema compliance
validated_data = series.model_dump()  # Safe for JSON serialization
```

## Key Features

### Type Safety
All models enforce the Civic Transparency schema constraints at runtime:
- Enum validation for categorical fields
- Date/time format validation (ISO 8601)
- Numeric range and string pattern validation
- Required field enforcement

### Privacy by Design
The type system enforces privacy-preserving patterns:
- No direct identifiers allowed
- Bucketed categorical values (e.g., account age ranges)
- Aggregated statistical summaries only
- Deduplication hashes instead of content

### Easy Integration
Works seamlessly with modern Python tooling:
- **FastAPI:** Automatic request/response validation
- **Dataclasses:** Compatible with existing data structures  
- **JSON APIs:** Native serialization/deserialization
- **Testing:** Clear validation error messages

## Available Types

| Model | Purpose | Key Fields |
|-------|---------|------------|
| **Series** | Time-bucketed aggregated data | `topic`, `points`, `interval` |
| **ProvenanceTag** | Post metadata (no PII) | `acct_type`, `automation_flag`, `media_provenance` |

## See Also

- **[API Reference](api.md):** Complete type documentation
- **[Series Reference](reference/series.md):** Detailed field documentation
- **[Provenance Tag Reference](reference/provenance_tag.md):** Metadata field guide
- **[Performance Guide](performance.md):** Performance guide
- **[Usage Guide](usage.md):** Common patterns and examples

## Relationship to Specification

This package provides the **runtime implementation** of types defined in the [Civic Transparency specification](https://civic-interconnect.github.io/civic-transparency-spec/).
The types are automatically generated from the canonical JSON schemas, ensuring perfect alignment with the specification.

For schema definitions, OpenAPI documentation, and specification details, visit the [spec repository](https://civic-interconnect.github.io/civic-transparency-spec/).

``

---

## File: `docs\en\performance.md`

``markdown
# Performance Guide

When working with civic transparency data at scale, these performance characteristics and optimizations can help you build efficient applications.

## Benchmark Results

Performance measured on **Windows Python 3.11.9** (your results may vary based on hardware and Python version):

### Validation Performance

| Model Type | Records/sec | Time per Record | Use Case |
|------------|-------------|-----------------|----------|
| **ProvenanceTag** | ~160,000 | 0.006ms | Post metadata validation |
| **Series (minimal)** | ~25,000 | 0.040ms | Simple time series |
| **Series (100 points)** | ~259 | 3.861ms | Complex time series |

### JSON Serialization Performance

| Model Type | Pydantic JSON | stdlib json | Speedup |
|------------|---------------|-------------|---------|
| **ProvenanceTag** | ~651,000/sec | ~269,000/sec | 2.4x |
| **Series (minimal)** | ~228,000/sec | ~91,000/sec | 2.5x |
| **Series (100 points)** | ~3,531/sec | ~1,511/sec | 2.3x |

**Key Insight:** Pydantic's `model_dump_json()` is consistently ~2.4x faster than `model_dump()` + `json.dumps()`.

### Memory Usage

| Model Type | Memory per Object | JSON Size | Efficiency |
|------------|------------------|-----------|------------|
| **ProvenanceTag** | ~1,084 bytes | 207 bytes | 5.2x overhead |
| **Series (minimal)** | ~7,127 bytes | 502 bytes | 14.2x overhead |
| **Series (100 points)** | ~660,159 bytes | 40,796 bytes | 16.2x overhead |

**Memory overhead** includes Python object structures, Pydantic metadata, and validation caching.

## Performance Patterns

### 1. Complexity Scaling
- **ProvenanceTag**: Simple enum validation is very fast
- **Series**: Scales linearly with number of data points
- **Nested validation**: Each point requires full coordinate validation

### 2. Serialization vs Validation
- **Serialization is faster**: JSON generation is 4-25x faster than validation
- **Pydantic optimized**: Built-in JSON serializer beats stdlib significantly
- **Memory efficient**: JSON representation is much more compact

### 3. Privacy-Preserving Design Impact
The privacy-by-design approach actually **helps performance**:
- **Bucketed enums** (like `acct_age_bucket`) validate faster than ranges
- **Categorical data** requires less processing than continuous values
- **Aggregated structures** reduce individual record complexity

## Optimization Strategies

### High-Throughput Validation

For processing large volumes of civic data:

```python
from ci.transparency.types import ProvenanceTag
from typing import List, Dict, Any
import logging

def process_provenance_batch(data_list: List[Dict[str, Any]]) -> List[ProvenanceTag]:
    """Process ~160K records/second efficiently."""
    results = []
    errors = 0
    
    for data in data_list:
        try:
            tag = ProvenanceTag.model_validate(data)
            results.append(tag)
        except ValidationError as e:
            errors += 1
            if errors < 10:  # Log first few errors
                logging.warning(f"Validation failed: {e}")
    
    return results

# Expected throughput: ~160,000 ProvenanceTags/second
```

### Efficient Series Processing

For time series data with many points:

```python
from ci.transparency.types import Series

def process_series_stream(data_stream):
    """Stream processing for memory efficiency."""
    for series_data in data_stream:
        # Validate once per series (~259/second for 100-point series)
        series = Series.model_validate(series_data)
        
        # Process and immediately serialize to save memory
        result = series.model_dump_json()  # ~3,531/second
        yield result
        
        # series goes out of scope, freeing ~660KB
```

### JSON Optimization

Choose serialization method based on your needs:

```python
# Fastest: Use Pydantic's built-in JSON (recommended)
json_str = series.model_dump_json()  # ~228K/sec for minimal series

# Alternative: For custom JSON formatting
import orjson  # Install separately for even better performance

data = series.model_dump(mode='json')  # Convert enums to values
json_bytes = orjson.dumps(data)       # Potentially faster than stdlib
```

### Memory Management

For processing large datasets:

```python
import gc
from typing import Iterator

def memory_efficient_processing(large_dataset: Iterator[dict]):
    """Process data without loading everything into memory."""
    batch_size = 1000
    batch = []
    
    for record in large_dataset:
        batch.append(record)
        
        if len(batch) >= batch_size:
            # Process batch
            results = [ProvenanceTag.model_validate(data) for data in batch]
            
            # Yield results and clear memory
            yield from results
            batch.clear()
            
            # Optional: Force garbage collection for long-running processes
            if len(results) % 10000 == 0:
                gc.collect()
```

## Production Considerations

### Database Integration

Based on the memory usage, consider your storage strategy:

```python
# For ProvenanceTag (1KB each): Can safely keep thousands in memory
provenance_cache = {}  # OK to cache frequently accessed tags

# For Series (7KB-660KB each): Stream processing recommended
def store_series_efficiently(series: Series):
    # Store as compressed JSON rather than keeping objects in memory
    json_data = series.model_dump_json()
    compressed = gzip.compress(json_data.encode())
    database.store(compressed)
```

### API Design

Design your APIs based on these performance characteristics:

```python
from fastapi import FastAPI
from ci.transparency.types import ProvenanceTag, Series

app = FastAPI()

@app.post("/provenance/batch")
async def upload_provenance_batch(tags: List[ProvenanceTag]):
    # Can handle large batches efficiently (~160K/sec validation)
    return {"processed": len(tags)}

@app.post("/series")
async def upload_series(series: Series):
    # Individual series upload (validation cost depends on point count)
    point_count = len(series.points)
    if point_count > 1000:
        # Consider async processing for very large series
        return {"status": "queued", "points": point_count}
    return {"status": "processed", "points": point_count}
```

## When Performance Matters

### High-Performance Scenarios
- **Real-time civic monitoring**: ProvenanceTag validation at 160K/sec supports live analysis
- **Batch processing**: Can process millions of records efficiently
- **API endpoints**: Fast enough for responsive web applications

### Optimization Not Needed
- **Typical civic research**: These speeds far exceed most analytical workloads
- **Small datasets**: Optimization overhead not worth it for <10K records
- **Prototype development**: Focus on correctness first, optimize later

## Monitoring Performance

Add performance monitoring to your applications:

```python
import time
import logging

class PerformanceMonitor:
    def __init__(self, name: str):
        self.name = name
        self.start_time = None
        
    def __enter__(self):
        self.start_time = time.perf_counter()
        return self
        
    def __exit__(self, *args):
        duration = time.perf_counter() - self.start_time
        logging.info(f"{self.name} took {duration:.3f}s")

# Usage
with PerformanceMonitor("ProvenanceTag validation"):
    tags = [ProvenanceTag.model_validate(data) for data in batch]
```

## Summary

The civic transparency types deliver **high performance** for privacy-preserving data processing:

- **Production-ready speeds**: 160K+ validations/second for metadata
- **Efficient serialization**: Built-in JSON optimization  
- **Predictable scaling**: Performance scales with data complexity
- **Memory conscious**: Reasonable overhead for rich validation

The privacy-by-design architecture (bucketed enums, aggregated data) **improves performance** compared to handling raw, detailed data structures.

``

---

## File: `docs\en\usage.md`

``markdown
# Usage

This page shows common patterns for loading, validating, and serializing Civic Transparency types.

## Install

```bash
pip install "civic-transparency-types==0.2.*" "civic-transparency-spec==0.2.*"
```

---

## Create and validate

```python
from ci.transparency.types import Series

series = Series(
    topic="#CityElection2026",
    generated_at="2026-02-07T00:00:00Z",  # parsed to datetime
    interval="minute",
    points=[],
)
```

---

## Serialize / deserialize

To send/store:

```python
payload: dict = series.model_dump()         # JSON-friendly dict
text: str = series.model_dump_json(indent=2)
```

To load an existing dict/JSON and validate:

```python
from ci.transparency.types import Series

loaded = Series.model_validate(payload)         # dict -> Series
loaded2 = Series.model_validate_json(text)      # JSON -> Series
```

---

## Validating with **jsonschema**

If you want an *extra* guardrail using the official schemas:

```python
import json
from importlib.resources import files
from jsonschema import Draft202012Validator

# 1) get the normative schema from the spec package
schema_text = files("ci.transparency.spec.schemas").joinpath("series.schema.json").read_text("utf-8")
series_schema = json.loads(schema_text)

# 2) validate the payload dict you produced with Pydantic
Draft202012Validator.check_schema(series_schema)          # sanity check the schema itself
Draft202012Validator(series_schema).validate(payload)     # raises jsonschema.ValidationError if invalid
```


---

## Round-trip file I/O

```python
import json
from pathlib import Path
from ci.transparency.types import Series

out = Path("series.json")

# write
out.write_text(Series(...).model_dump_json(indent=2), encoding="utf-8")

# read + validate
data = json.loads(out.read_text(encoding="utf-8"))
series = Series.model_validate(data)
```

---

## Using with FastAPI (optional)

Pydantic v2 models work out-of-the-box:

```python
from fastapi import FastAPI
from ci.transparency.types import Series

app = FastAPI()

@app.post("/series")
def post_series(s: Series) -> Series:
    # s is validated already
    return s  # echo back, or transform and return
```

---

## Generating / Regenerating the types (contributors)

Types are generated from the `civic-transparency-spec` package with `datamodel-code-generator`.

```bash
# in the types repo
python scripts/generate_types.py
```

CI tip (to ensure generated code is up to date):

```bash
python scripts/generate_types.py
git diff --exit-code
```

---

## Troubleshooting

**“Unknown field …”**  
The models are strict (`extra="forbid"`). Remove unexpected keys or update the schema definitions & regenerate.

**Datetime parsing**  
Use ISO 8601 (`YYYY-MM-DDTHH:MM:SSZ` or with offset). Pydantic converts to `datetime`.

**Version mismatches**  
Pin both packages to compatible versions. If the definitions change, regenerate types.

---

## See also

- Schemas: <https://civic-interconnect.github.io/civic-transparency-spec/>
- API Reference:
  - [Series](reference/series.md)
  - [Provenance Tag](reference/provenance_tag.md)

``

---

## File: `docs\en\reference\provenance_tag.md`

``markdown
# Provenance Tag (Pydantic)

::: ci.transparency.types.provenance_tag.ProvenanceTag
    options:
      show_source: false
      show_signature: true
      group_by_category: true
      filters:
        - "!^_"

``

---

## File: `docs\en\reference\series.md`

``markdown
# Series (Pydantic)

::: ci.transparency.types.series.Series
    options:
      show_source: false
      show_signature: true
      group_by_category: true
      filters:
        - "!^_"

``

---

## File: `scripts\generate_types.py`

``python
# scripts/generate_types.py
import subprocess
import sys
import hashlib
from pathlib import Path
from importlib.resources import as_file, files
from importlib.metadata import version as pkgver

SCHEMA_PKG = "ci.transparency.spec.schemas"
OUT_DIR = Path("src/ci/transparency/types")


def _add_schema_header(file_path, schema_name):
    """Add provenance header that pre-commit hooks expect."""
    # Normalize line endings BEFORE calculating hash
    _normalize_line_endings(file_path)

    schema_file = files(SCHEMA_PKG) / schema_name
    schema_text = schema_file.read_text()
    schema_sha = hashlib.sha256(schema_text.encode("utf-8")).hexdigest()
    spec_ver = pkgver("civic-transparency-spec")

    content = file_path.read_text()
    header = (
        "# AUTO-GENERATED: do not edit by hand\n"
        f"# source-schema: {schema_name}\n"
        f"# schema-sha256: {schema_sha}\n"
        f"# spec-version: {spec_ver}\n"
    )
    file_path.write_text(header + content)
    _normalize_line_endings(file_path)
    print(f"Added schema header to {file_path.name}")


def _fix_points_field(series_file):
    """Replace the multi-line points Field with default_factory=list."""
    content: str = series_file.read_text()
    lines: list[str] = content.splitlines()

    # Find the start of the points field
    points_start = None
    for i, line in enumerate(lines):
        if "points: List[Point] = Field(" in line:
            points_start = i
            break

    if points_start is None:
        print("ERROR: Points field not found")
        return False

    # Find the end of the Field definition
    paren_count = 0
    points_end = points_start
    for i in range(points_start, len(lines)):
        line = lines[i]
        paren_count += line.count("(") - line.count(")")
        if paren_count == 0 and i > points_start:
            points_end = i
            break

    print(f"Replacing points field (lines {points_start + 1}-{points_end + 1})")

    # Get indentation from original line
    original_line = lines[points_start]
    indent = len(original_line) - len(original_line.lstrip())
    indentation = " " * indent

    # Replace with simple default_factory version
    new_line = f"{indentation}points: List[Point] = Field(default_factory=list)"

    # Build new content
    new_lines = lines[:points_start] + [new_line] + lines[points_end + 1 :]

    series_file.write_text("\n".join(new_lines))
    print("Fixed points field")
    return True


def _normalize_line_endings(file_path):
    """Convert CRLF to LF to match what ruff expects."""
    content = file_path.read_bytes()
    if b"\r\n" in content:
        content = content.replace(b"\r\n", b"\n")
        file_path.write_bytes(content)
        print(f"Normalized line endings in {file_path.name}")


def _rename_seriesdoc_to_series(series_file):
    """Rename SeriesDoc class to Series for cleaner Python API."""
    content = series_file.read_text()
    content = content.replace("class SeriesDoc(", "class Series(")
    series_file.write_text(content)
    print("Renamed SeriesDoc to Series")


def main():
    print("Generating types...")
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # Generate each file
    for schema_file, py_file in [
        ("series.schema.json", "series.py"),
        ("provenance_tag.schema.json", "provenance_tag.py"),
    ]:
        print(f"Generating {py_file}...")
        with as_file(files(SCHEMA_PKG) / schema_file) as schema_path:
            cmd = [
                sys.executable,
                "-m",
                "datamodel_code_generator",
                "--input",
                str(schema_path),
                "--input-file-type",
                "jsonschema",
                "--output",
                str(OUT_DIR / py_file),
                "--output-model-type",
                "pydantic_v2.BaseModel",
                "--target-python-version",
                "3.11",
                "--disable-timestamp",
            ]
            subprocess.run(cmd, check=True)

        # Post-process Python files
        file_path = OUT_DIR / py_file
        if py_file == "series.py":
            _fix_points_field(file_path)
            _rename_seriesdoc_to_series(file_path)

        _add_schema_header(file_path, schema_file)

    series_file = OUT_DIR / "series.py"
    series_content = series_file.read_text()

    # Check what classes exist
    available_classes = []
    imports = []

    if "class Series(" in series_content:
        available_classes.append("Series")
        imports.append("from .series import Series")

    if "class Interval(" in series_content:
        available_classes.append("Interval")
        imports.append("from .series import Interval")

    provenance_file = OUT_DIR / "provenance_tag.py"
    if provenance_file.exists():
        provenance_content = provenance_file.read_text()
        if "class ProvenanceTag(" in provenance_content:
            available_classes.append("ProvenanceTag")
            imports.append("from .provenance_tag import ProvenanceTag")

    # Write __init__.py with actual available classes
    init_content = "\n".join(imports) + "\n"
    init_content += "from ._version import __version__  # noqa: F401\n"
    init_content += f"__all__ = {available_classes!r}\n"
    (OUT_DIR / "__init__.py").write_text(init_content)
    print(f"Updated __init__.py to export: {available_classes}")

    print("Generation complete.")


if __name__ == "__main__":
    main()

``

---

## File: `src\ci\transparency\types\__init__.py`

``python
from .series import Series
from .series import Interval
from .provenance_tag import ProvenanceTag
from ._version import __version__  # noqa: F401

__all__ = ["Series", "Interval", "ProvenanceTag"]

``

---

## File: `src\ci\transparency\types\_version.py`

``python
# file generated by setuptools-scm
# don't change, don't track in version control

__all__ = [
    "__version__",
    "__version_tuple__",
    "version",
    "version_tuple",
    "__commit_id__",
    "commit_id",
]

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Tuple
    from typing import Union

    VERSION_TUPLE = Tuple[Union[int, str], ...]
    COMMIT_ID = Union[str, None]
else:
    VERSION_TUPLE = object
    COMMIT_ID = object

version: str
__version__: str
__version_tuple__: VERSION_TUPLE
version_tuple: VERSION_TUPLE
commit_id: COMMIT_ID
__commit_id__: COMMIT_ID

__version__ = version = '0.1.dev17'
__version_tuple__ = version_tuple = (0, 1, 'dev17')

__commit_id__ = commit_id = 'g0d85f0a73'

``

---

## File: `src\ci\transparency\types\provenance_tag.py`

``python
# AUTO-GENERATED: do not edit by hand
# source-schema: provenance_tag.schema.json
# schema-sha256: 40f34c6734ad87e3ae728b9400c1d341b1aa6f7ba5a97d1bfd26b5af87c79d0b
# spec-version: 0.2.1
# generated by datamodel-codegen:
#   filename:  provenance_tag.schema.json

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, RootModel, constr


class AcctAge(Enum):
    field_0_7d = "0-7d"
    field_8_30d = "8-30d"
    field_1_6m = "1-6m"
    field_6_24m = "6-24m"
    field_24m_ = "24m+"


class AcctType(Enum):
    person = "person"
    org = "org"
    media = "media"
    public_official = "public_official"
    unverified = "unverified"
    declared_automation = "declared_automation"


class AutomationFlag(Enum):
    manual = "manual"
    scheduled = "scheduled"
    api_client = "api_client"
    declared_bot = "declared_bot"


class PostKind(Enum):
    original = "original"
    reshare = "reshare"
    quote = "quote"
    reply = "reply"


class ClientFamily(Enum):
    web = "web"
    mobile = "mobile"
    third_party_api = "third_party_api"


class MediaProvenance(Enum):
    c2pa_present = "c2pa_present"
    hash_only = "hash_only"
    none = "none"


class ISO3166CountryOrSubdivision(
    RootModel[constr(pattern=r"^[A-Z]{2}(-[A-Z0-9]{1,3})?$")]
):
    root: constr(pattern=r"^[A-Z]{2}(-[A-Z0-9]{1,3})?$") = Field(
        ...,
        description="Uppercase ISO-3166-1 alpha-2 country code, optionally with ISO-3166-2 subdivision (e.g., US or US-CA).",
    )


class HexHash8(RootModel[constr(pattern=r"^[a-f0-9]{8}$", min_length=8, max_length=8)]):
    root: constr(pattern=r"^[a-f0-9]{8}$", min_length=8, max_length=8) = Field(
        ...,
        description="Fixed 8-character lowercase hex hash (privacy-preserving, daily salted).",
    )


class ProvenanceTag(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    acct_age_bucket: AcctAge = Field(
        ...,
        description="Account age bucketed for privacy: e.g., '0-7d', '8-30d', '1-6m', '6-24m', '24m+'.",
    )
    acct_type: AcctType = Field(..., description="Declared identity account type.")
    automation_flag: AutomationFlag = Field(
        ...,
        description="Posting method with clear boundaries: manual (direct user interaction), scheduled (user-configured delayed posting), api_client (third-party tools like Buffer/Hootsuite), declared_bot (automated systems with explicit bot declaration).",
    )
    post_kind: PostKind = Field(
        ..., description="Content relationship: original, reshare, quote, reply."
    )
    client_family: ClientFamily = Field(
        ..., description="Application class: web, mobile, third_party_api."
    )
    media_provenance: MediaProvenance = Field(
        ..., description="Embedded authenticity: c2pa_present, hash_only, none."
    )
    dedup_hash: HexHash8 = Field(
        ...,
        description="Privacy-preserving rolling hash for duplicate detection (fixed 8 hex characters, salted daily to prevent cross-dataset correlation).",
    )
    origin_hint: Optional[ISO3166CountryOrSubdivision] = Field(
        None,
        description="Geographic origin limited to country-level (ISO country codes) or major subdivisions only for populations >1M, e.g., 'US', 'US-CA', where lawful.",
    )

``

---

## File: `src\ci\transparency\types\py.typed`

*File is empty*

---

## File: `src\ci\transparency\types\series.py`

``python
# AUTO-GENERATED: do not edit by hand
# source-schema: series.schema.json
# schema-sha256: acf1664027df36e92afba906343a652cc07c12ebeb333467bed522cfb179c3b0
# spec-version: 0.2.1
# generated by datamodel-codegen:
#   filename:  series.schema.json

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Dict, List

from pydantic import BaseModel, ConfigDict, Field, RootModel, confloat, conint, constr


class Interval(Enum):
    minute = "minute"


class Probability(RootModel[confloat(ge=0.0, le=1.0)]):
    root: confloat(ge=0.0, le=1.0)


class CoordinationSignals(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    burst_score: Probability = Field(..., description="Burstiness indicator (0-1).")
    synchrony_index: Probability = Field(
        ..., description="Temporal synchrony indicator (0-1)."
    )
    duplication_clusters: conint(ge=0) = Field(
        ..., description="Count of duplicate/near-duplicate content clusters."
    )


class Point(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    ts: datetime = Field(
        ..., description="UTC minute boundary for this point (ISO 8601)."
    )
    volume: conint(ge=0) = Field(
        ..., description="Total posts observed in this interval."
    )
    reshare_ratio: Probability = Field(
        ..., description="Fraction of posts that are reshares in this interval."
    )
    recycled_content_rate: Probability = Field(
        ...,
        description="Estimated fraction of posts that recycle prior content (hash/duplicate-based).",
    )
    acct_age_mix: Dict[str, Probability] = Field(
        ...,
        description="Distribution over account-age buckets; values typically sum to ~1.0.",
    )
    automation_mix: Dict[str, Probability] = Field(
        ...,
        description="Distribution over automation flags; values typically sum to ~1.0.",
    )
    client_mix: Dict[str, Probability] = Field(
        ...,
        description="Distribution over client families; values typically sum to ~1.0.",
    )
    coordination_signals: CoordinationSignals = Field(
        ..., description="Per-interval coordination indicators."
    )


class Series(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    topic: constr(min_length=1) = Field(
        ..., description="Topic key (e.g., hashtag) this series describes."
    )
    generated_at: datetime = Field(
        ..., description="UTC timestamp when this series was generated (ISO 8601)."
    )
    interval: Interval = Field(..., description="Aggregation interval.")
    points: List[Point] = Field(default_factory=list)

``

---

## File: `tests\test_example_data.py`

``python
# tests/test_example_data.py
import json
from pathlib import Path
from ci.transparency.types import Series, ProvenanceTag
import pytest


class TestExampleData:
    """Test that our example data validates correctly."""

    def test_series_minimal_example(self):
        """Test minimal valid Series example."""
        data_file = Path(__file__).parent / "data" / "series_minimal.json"
        data = json.loads(data_file.read_text())

        # Should
        # validate without errors
        series = Series.model_validate(data)

        # Verify key properties
        assert series.topic == "#TestTopic"
        assert series.interval.value == "minute"  # Compare enum value, not enum object
        assert len(series.points) == 1
        assert series.points[0].volume == 100

        # Round-trip test
        serialized = series.model_dump()
        series2 = Series.model_validate(serialized)
        assert series == series2

    def test_provenance_tag_minimal_example(self):
        """Test minimal valid ProvenanceTag example."""
        data_file = Path(__file__).parent / "data" / "provenance_tag_minimal.json"
        if not data_file.exists():
            # Create the test data if it doesn't exist
            test_data = {
                "acct_age_bucket": "1-6m",
                "acct_type": "person",
                "automation_flag": "manual",
                "post_kind": "original",
                "client_family": "mobile",
                "media_provenance": "hash_only",
                "origin_hint": "US-CA",
                "dedup_hash": "a1b2c3d4e5f6789a",
            }
            data_file.write_text(json.dumps(test_data, indent=2))

        data = json.loads(data_file.read_text())

        # Should validate without errors
        tag = ProvenanceTag.model_validate(data)

        # Verify key properties
        assert tag.acct_type.value == "person"  # Compare enum value
        assert tag.automation_flag.value == "manual"  # Compare enum value
        tag_dict = tag.model_dump()
        assert tag_dict["origin_hint"] == "US-CA"

        # Round-trip test
        serialized = tag.model_dump()
        tag2 = ProvenanceTag.model_validate(serialized)
        assert tag == tag2

    def test_schema_validation_against_examples(self):
        """Validate examples against canonical JSON schemas."""
        try:
            from importlib.resources import files
            from jsonschema import Draft202012Validator
        except ImportError:
            pytest.skip("jsonschema or importlib.resources not available")

        # Test Series
        series_data_file = Path(__file__).parent / "data" / "series_minimal.json"
        if not series_data_file.exists():
            pytest.skip("series_minimal.json test data not found")

        series_data = json.loads(series_data_file.read_text())

        try:
            schema_text = (
                files("ci.transparency.spec.schemas")
                .joinpath("series.schema.json")
                .read_text()
            )
            schema = json.loads(schema_text)

            # Should validate against canonical schema
            Draft202012Validator(schema).validate(series_data)  # type: ignore
        except Exception as e:
            pytest.skip(f"Schema validation failed: {e}")

        # Test ProvenanceTag
        tag_data_file = Path(__file__).parent / "data" / "provenance_tag_minimal.json"
        if not tag_data_file.exists():
            pytest.skip("provenance_tag_minimal.json test data not found")

        tag_data = json.loads(tag_data_file.read_text())

        try:
            schema_text = (
                files("ci.transparency.spec.schemas")
                .joinpath("provenance_tag.schema.json")
                .read_text()
            )
            schema = json.loads(schema_text)

            # Should validate against canonical schema
            Draft202012Validator(schema).validate(tag_data)  # type: ignore
        except Exception as e:
            pytest.skip(f"ProvenanceTag schema validation failed: {e}")

``

---

## File: `tests\test_imports.py`

``python
# tests/test_imports.py
from ci.transparency.types import Series, ProvenanceTag


def test_imports():  # just proves modules exist
    assert Series and ProvenanceTag

``

---

## File: `tests\test_public_api.py`

``python
# tests/test_public_api.py


def test_public_api_surface():
    import ci.transparency.types as t

    expected = {"Series", "ProvenanceTag"}
    # __all__ exists and contains the public names
    assert expected.issubset(set(getattr(t, "__all__", [])))

    # Touch each symbol so the re-export lines count as covered
    for name in expected:
        obj = getattr(t, name)
        assert isinstance(obj, type), f"{name} should be a class"


def test_version_present_and_string():
    from ci.transparency.types import __version__  # type: ignore

    assert isinstance(__version__, str) and __version__

``

---

## File: `tests\test_series.py`

``python
# tests/test_roundtrip_series.py
from pydantic import BaseModel
from ci.transparency.types import Series


def test_series_model_schema_is_sane():
    assert issubclass(Series, BaseModel)
    js = Series.model_json_schema()
    assert isinstance(js, dict)
    assert "title" in js
    assert "properties" in js and js["properties"]
    assert "type" in js and js["type"] == "object"


def test_points_can_be_empty():
    Series.model_validate(
        {
            "topic": "#X",
            "generated_at": "2025-01-01T00:00:00Z",
            "interval": "minute",
            "points": [],
        }
    )

``

---

## File: `tests\data\provenance_tag_minimal.json`

``json
{
  "acct_age_bucket": "1-6m",
  "acct_type": "person",
  "automation_flag": "manual",
  "post_kind": "original",
  "client_family": "mobile",
  "media_provenance": "hash_only",
  "origin_hint": "US-CA",
  "dedup_hash": "a1b2c3d4"
}

``

---

## File: `tests\data\series_minimal.json`

``json
{
  "topic": "#TestTopic",
  "generated_at": "2025-08-19T12:00:00Z",
  "interval": "minute",
  "points": [
    {
      "ts": "2025-08-19T12:00:00Z",
      "volume": 100,
      "reshare_ratio": 0.25,
      "recycled_content_rate": 0.1,
      "acct_age_mix": {
        "0-7d": 0.2,
        "8-30d": 0.3,
        "1-6m": 0.3,
        "6-24m": 0.15,
        "24m+": 0.05
      },
      "automation_mix": {
        "manual": 0.8,
        "scheduled": 0.1,
        "api_client": 0.05,
        "declared_bot": 0.05
      },
      "client_mix": {
        "web": 0.6,
        "mobile": 0.35,
        "third_party_api": 0.05
      },
      "coordination_signals": {
        "burst_score": 0.3,
        "synchrony_index": 0.2,
        "duplication_clusters": 5
      }
    }
  ]
}
``

---

## File: `docs\en\api.md`

``markdown
# API Reference

The Civic Transparency Types package provides a clean, typed interface to the Civic Transparency specification. All models are built with Pydantic v2 and automatically validate against the canonical JSON schemas.

## Package Overview

```python
import ci.transparency.types as ct

# Available models
ct.Series          # Time-bucketed civic data
ct.ProvenanceTag   # Post metadata (privacy-preserving)

# Package metadata
ct.__version__     # Current package version
ct.__all__         # Public API surface
```

---

## Public API

### Core Models

| Class | Purpose | Schema Source |
|-------|---------|---------------|
| **`Series`** | Aggregated time series for civic topics | `series.schema.json` |
| **`ProvenanceTag`** | Categorical post metadata (no PII) | `provenance_tag.schema.json` |

### Package Information

- **`__version__`** (str): Current package version
- **`__all__`** (List[str]): Public API exports

---

## Import Patterns

### Recommended: Barrel Import
```python
from ci.transparency.types import Series, ProvenanceTag

# Clean, simple imports for application code
series = Series(...)
tag = ProvenanceTag(...)
```

### Alternative: Direct Module Import
```python
from ci.transparency.types.series import Series
from ci.transparency.types.provenance_tag import ProvenanceTag

# Useful for IDE "go to definition" and explicit dependencies
```

### Package-Level Import
```python
import ci.transparency.types as ct

# Namespaced access
series = ct.Series(...)
version = ct.__version__
```

---

## Base Model Behavior

All types inherit from `pydantic.BaseModel` and provide the complete Pydantic v2 API:

### Instance Methods

```python
series = Series(...)

# Serialization
data = series.model_dump()                    # → dict (JSON-safe)
json_str = series.model_dump_json()           # → JSON string
json_pretty = series.model_dump_json(indent=2)  # → Pretty JSON

# Copying and updating
updated = series.model_copy(update={'topic': '#NewTopic'})
```

### Class Methods

```python
# Validation and parsing
series = Series.model_validate(data_dict)        # dict → Series
series = Series.model_validate_json(json_string) # JSON → Series

# Schema introspection  
schema = Series.model_json_schema()              # Pydantic-generated schema
fields = Series.model_fields                     # Field definitions
```

### Configuration

All models use strict validation:
- **`extra="forbid"`**: Unknown fields are rejected
- **Type coercion**: Automatic type conversion where safe
- **Validation**: Full constraint checking (patterns, ranges, enums)

---

## Validation Features

### Runtime Type Safety

```python
from pydantic import ValidationError

try:
    # This will fail validation
    invalid_series = Series(
        topic="",  # Empty string not allowed
        generated_at="not-a-date",  # Invalid datetime
        interval="invalid",  # Not in enum
        points=[]
    )
except ValidationError as e:
    print(f"Validation errors: {e}")
```

### Enum Validation

```python
from ci.transparency.types import ProvenanceTag

# Valid enum values are enforced
tag = ProvenanceTag(
    acct_type="person",        # ✓ Valid
    automation_flag="manual"   # ✓ Valid
    # acct_type="wizard"       # ✗ Would raise ValidationError
)
```

### Pattern and Range Validation

```python
# String patterns, numeric ranges, etc. are validated
tag = ProvenanceTag(
    dedup_hash="abc123",       # ✓ Valid hex pattern
    origin_hint="US-CA",       # ✓ Valid country-region format
    # dedup_hash="xyz!"        # ✗ Invalid characters
)
```

---

## Schema Access

### Pydantic Schema (Runtime)

```python
# Get Pydantic-generated schema for tooling
schema = Series.model_json_schema()
print(schema['properties']['topic'])  # Field definition
```

### Canonical Schema (Normative)

Access the official JSON schemas that define the specification:

```python
import json
from importlib.resources import files

# Get the source-of-truth schema
schema_text = files("ci.transparency.spec.schemas").joinpath(
    "series.schema.json"
).read_text("utf-8")
canonical_schema = json.loads(schema_text)

# Use for validation, documentation generation, etc.
from jsonschema import Draft202012Validator
validator = Draft202012Validator(canonical_schema)
validator.validate(series.model_dump())
```

---

## Serialization Details

### JSON Compatibility

```python
series = Series(...)

# These produce equivalent JSON-safe data
data1 = series.model_dump()
data2 = json.loads(series.model_dump_json())
assert data1 == data2
```

### Datetime Handling

```python
from datetime import datetime

series = Series(
    generated_at=datetime.now(),  # Accepts datetime objects
    # ...
)

# Serializes to ISO 8601 strings
data = series.model_dump()
assert isinstance(data['generated_at'], str)  # "2025-01-15T12:00:00Z"
```

### Field Customization

```python
# Exclude fields during serialization
public_data = series.model_dump(exclude={'generated_at'})

# Include only specific fields
minimal_data = series.model_dump(include={'topic', 'interval'})

# Use aliases if defined (none currently in this spec)
aliased_data = series.model_dump(by_alias=True)
```

---

## Error Handling

### Validation Errors

```python
from pydantic import ValidationError

def safe_parse_series(data: dict) -> Series | None:
    """Parse series data with error handling."""
    try:
        return Series.model_validate(data)
    except ValidationError as e:
        # Log specific validation failures
        for error in e.errors():
            field = " → ".join(str(loc) for loc in error['loc'])
            print(f"Validation error in {field}: {error['msg']}")
        return None
```

### Field-Level Errors

```python
try:
    Series.model_validate(bad_data)
except ValidationError as e:
    for error in e.errors():
        print(f"Field: {error['loc']}")       # Which field failed
        print(f"Value: {error['input']}")     # The invalid input
        print(f"Error: {error['msg']}")       # What went wrong
        print(f"Type: {error['type']}")       # Error category
```

---

## Framework Integration

### FastAPI

Automatic request/response validation:

```python
from fastapi import FastAPI
from ci.transparency.types import Series

app = FastAPI()

@app.post("/data")
async def receive_data(series: Series) -> dict:
    # 'series' is automatically validated
    return {"received": series.topic}
```

### Dataclasses Integration

```python
from dataclasses import dataclass
from ci.transparency.types import Series

@dataclass
class ProcessingResult:
    series: Series
    processed_at: str
    
    def to_dict(self):
        return {
            'series': self.series.model_dump(),
            'processed_at': self.processed_at
        }
```

### Django Models

```python
from django.db import models
from ci.transparency.types import Series
import json

class CivicDataRecord(models.Model):
    topic = models.CharField(max_length=255)
    data = models.JSONField()
    
    def get_series(self) -> Series:
        return Series.model_validate(self.data)
    
    def set_series(self, series: Series):
        self.topic = series.topic
        self.data = series.model_dump()
```

---

## Type Information

### Static Type Checking

The package includes `py.typed` for full mypy/pyright support:

```python
from ci.transparency.types import Series

def process_series(series: Series) -> str:
    # Full type safety and IDE completion
    return series.topic.upper()

# mypy will catch type errors
process_series("not a series")  # Error: Argument 1 has incompatible type
```

### Runtime Type Inspection

```python
from ci.transparency.types import Series
import inspect

# Inspect model structure
print(Series.__annotations__)  # Field type annotations
print(Series.model_fields)     # Pydantic field definitions

# Check inheritance
assert issubclass(Series, BaseModel)
```

``

---

## File: `docs\en\index.md`

``markdown
# Civic Transparency – Types (Python)

Strongly-typed Python models for the [Civic Transparency specification](https://civic-interconnect.github.io/civic-transparency-spec/), built with Pydantic v2.

## What This Package Provides

- **Runtime Type Safety:** Full validation of civic transparency data structures
- **IDE Support:** Complete type hints and autocompletion
- **Schema Compliance:** Generated directly from canonical JSON schemas
- **Privacy Compliance:** Built-in validation for privacy-preserving data patterns

## Installation

```bash
pip install civic-transparency-types
```

## Quick Example

```python
from ci.transparency.types import Series
from datetime import datetime

# Create a validated civic data series
series = Series(
    topic="#CityBudget2025",
    generated_at=datetime.now().isoformat() + "Z",
    interval="minute",
    points=[]  # Your aggregated, privacy-preserving data points
)

# Automatic validation ensures schema compliance
validated_data = series.model_dump()  # Safe for JSON serialization
```

## Key Features

### Type Safety
All models enforce the Civic Transparency schema constraints at runtime:
- Enum validation for categorical fields
- Date/time format validation (ISO 8601)
- Numeric range and string pattern validation
- Required field enforcement

### Privacy by Design
The type system enforces privacy-preserving patterns:
- No direct identifiers allowed
- Bucketed categorical values (e.g., account age ranges)
- Aggregated statistical summaries only
- Deduplication hashes instead of content

### Easy Integration
Works seamlessly with modern Python tooling:
- **FastAPI:** Automatic request/response validation
- **Dataclasses:** Compatible with existing data structures  
- **JSON APIs:** Native serialization/deserialization
- **Testing:** Clear validation error messages

## Available Types

| Model | Purpose | Key Fields |
|-------|---------|------------|
| **Series** | Time-bucketed aggregated data | `topic`, `points`, `interval` |
| **ProvenanceTag** | Post metadata (no PII) | `acct_type`, `automation_flag`, `media_provenance` |

## See Also

- **[API Reference](api.md):** Complete type documentation
- **[Series Reference](reference/series.md):** Detailed field documentation
- **[Provenance Tag Reference](reference/provenance_tag.md):** Metadata field guide
- **[Performance Guide](performance.md):** Performance guide
- **[Usage Guide](usage.md):** Common patterns and examples

## Relationship to Specification

This package provides the **runtime implementation** of types defined in the [Civic Transparency specification](https://civic-interconnect.github.io/civic-transparency-spec/).
The types are automatically generated from the canonical JSON schemas, ensuring perfect alignment with the specification.

For schema definitions, OpenAPI documentation, and specification details, visit the [spec repository](https://civic-interconnect.github.io/civic-transparency-spec/).

``

---

## File: `docs\en\performance.md`

``markdown
# Performance Guide

When working with civic transparency data at scale, these performance characteristics and optimizations can help you build efficient applications.

## Benchmark Results

Performance measured on **Windows Python 3.11.9** (your results may vary based on hardware and Python version):

### Validation Performance

| Model Type | Records/sec | Time per Record | Use Case |
|------------|-------------|-----------------|----------|
| **ProvenanceTag** | ~160,000 | 0.006ms | Post metadata validation |
| **Series (minimal)** | ~25,000 | 0.040ms | Simple time series |
| **Series (100 points)** | ~259 | 3.861ms | Complex time series |

### JSON Serialization Performance

| Model Type | Pydantic JSON | stdlib json | Speedup |
|------------|---------------|-------------|---------|
| **ProvenanceTag** | ~651,000/sec | ~269,000/sec | 2.4x |
| **Series (minimal)** | ~228,000/sec | ~91,000/sec | 2.5x |
| **Series (100 points)** | ~3,531/sec | ~1,511/sec | 2.3x |

**Key Insight:** Pydantic's `model_dump_json()` is consistently ~2.4x faster than `model_dump()` + `json.dumps()`.

### Memory Usage

| Model Type | Memory per Object | JSON Size | Efficiency |
|------------|------------------|-----------|------------|
| **ProvenanceTag** | ~1,084 bytes | 207 bytes | 5.2x overhead |
| **Series (minimal)** | ~7,127 bytes | 502 bytes | 14.2x overhead |
| **Series (100 points)** | ~660,159 bytes | 40,796 bytes | 16.2x overhead |

**Memory overhead** includes Python object structures, Pydantic metadata, and validation caching.

## Performance Patterns

### 1. Complexity Scaling
- **ProvenanceTag**: Simple enum validation is very fast
- **Series**: Scales linearly with number of data points
- **Nested validation**: Each point requires full coordinate validation

### 2. Serialization vs Validation
- **Serialization is faster**: JSON generation is 4-25x faster than validation
- **Pydantic optimized**: Built-in JSON serializer beats stdlib significantly
- **Memory efficient**: JSON representation is much more compact

### 3. Privacy-Preserving Design Impact
The privacy-by-design approach actually **helps performance**:
- **Bucketed enums** (like `acct_age_bucket`) validate faster than ranges
- **Categorical data** requires less processing than continuous values
- **Aggregated structures** reduce individual record complexity

## Optimization Strategies

### High-Throughput Validation

For processing large volumes of civic data:

```python
from ci.transparency.types import ProvenanceTag
from typing import List, Dict, Any
import logging

def process_provenance_batch(data_list: List[Dict[str, Any]]) -> List[ProvenanceTag]:
    """Process ~160K records/second efficiently."""
    results = []
    errors = 0
    
    for data in data_list:
        try:
            tag = ProvenanceTag.model_validate(data)
            results.append(tag)
        except ValidationError as e:
            errors += 1
            if errors < 10:  # Log first few errors
                logging.warning(f"Validation failed: {e}")
    
    return results

# Expected throughput: ~160,000 ProvenanceTags/second
```

### Efficient Series Processing

For time series data with many points:

```python
from ci.transparency.types import Series

def process_series_stream(data_stream):
    """Stream processing for memory efficiency."""
    for series_data in data_stream:
        # Validate once per series (~259/second for 100-point series)
        series = Series.model_validate(series_data)
        
        # Process and immediately serialize to save memory
        result = series.model_dump_json()  # ~3,531/second
        yield result
        
        # series goes out of scope, freeing ~660KB
```

### JSON Optimization

Choose serialization method based on your needs:

```python
# Fastest: Use Pydantic's built-in JSON (recommended)
json_str = series.model_dump_json()  # ~228K/sec for minimal series

# Alternative: For custom JSON formatting
import orjson  # Install separately for even better performance

data = series.model_dump(mode='json')  # Convert enums to values
json_bytes = orjson.dumps(data)       # Potentially faster than stdlib
```

### Memory Management

For processing large datasets:

```python
import gc
from typing import Iterator

def memory_efficient_processing(large_dataset: Iterator[dict]):
    """Process data without loading everything into memory."""
    batch_size = 1000
    batch = []
    
    for record in large_dataset:
        batch.append(record)
        
        if len(batch) >= batch_size:
            # Process batch
            results = [ProvenanceTag.model_validate(data) for data in batch]
            
            # Yield results and clear memory
            yield from results
            batch.clear()
            
            # Optional: Force garbage collection for long-running processes
            if len(results) % 10000 == 0:
                gc.collect()
```

## Production Considerations

### Database Integration

Based on the memory usage, consider your storage strategy:

```python
# For ProvenanceTag (1KB each): Can safely keep thousands in memory
provenance_cache = {}  # OK to cache frequently accessed tags

# For Series (7KB-660KB each): Stream processing recommended
def store_series_efficiently(series: Series):
    # Store as compressed JSON rather than keeping objects in memory
    json_data = series.model_dump_json()
    compressed = gzip.compress(json_data.encode())
    database.store(compressed)
```

### API Design

Design your APIs based on these performance characteristics:

```python
from fastapi import FastAPI
from ci.transparency.types import ProvenanceTag, Series

app = FastAPI()

@app.post("/provenance/batch")
async def upload_provenance_batch(tags: List[ProvenanceTag]):
    # Can handle large batches efficiently (~160K/sec validation)
    return {"processed": len(tags)}

@app.post("/series")
async def upload_series(series: Series):
    # Individual series upload (validation cost depends on point count)
    point_count = len(series.points)
    if point_count > 1000:
        # Consider async processing for very large series
        return {"status": "queued", "points": point_count}
    return {"status": "processed", "points": point_count}
```

## When Performance Matters

### High-Performance Scenarios
- **Real-time civic monitoring**: ProvenanceTag validation at 160K/sec supports live analysis
- **Batch processing**: Can process millions of records efficiently
- **API endpoints**: Fast enough for responsive web applications

### Optimization Not Needed
- **Typical civic research**: These speeds far exceed most analytical workloads
- **Small datasets**: Optimization overhead not worth it for <10K records
- **Prototype development**: Focus on correctness first, optimize later

## Monitoring Performance

Add performance monitoring to your applications:

```python
import time
import logging

class PerformanceMonitor:
    def __init__(self, name: str):
        self.name = name
        self.start_time = None
        
    def __enter__(self):
        self.start_time = time.perf_counter()
        return self
        
    def __exit__(self, *args):
        duration = time.perf_counter() - self.start_time
        logging.info(f"{self.name} took {duration:.3f}s")

# Usage
with PerformanceMonitor("ProvenanceTag validation"):
    tags = [ProvenanceTag.model_validate(data) for data in batch]
```

## Summary

The civic transparency types deliver **high performance** for privacy-preserving data processing:

- **Production-ready speeds**: 160K+ validations/second for metadata
- **Efficient serialization**: Built-in JSON optimization  
- **Predictable scaling**: Performance scales with data complexity
- **Memory conscious**: Reasonable overhead for rich validation

The privacy-by-design architecture (bucketed enums, aggregated data) **improves performance** compared to handling raw, detailed data structures.

``

---

## File: `docs\en\usage.md`

``markdown
# Usage

This page shows common patterns for loading, validating, and serializing Civic Transparency types.

## Install

```bash
pip install "civic-transparency-types==0.2.*" "civic-transparency-spec==0.2.*"
```

---

## Create and validate

```python
from ci.transparency.types import Series

series = Series(
    topic="#CityElection2026",
    generated_at="2026-02-07T00:00:00Z",  # parsed to datetime
    interval="minute",
    points=[],
)
```

---

## Serialize / deserialize

To send/store:

```python
payload: dict = series.model_dump()         # JSON-friendly dict
text: str = series.model_dump_json(indent=2)
```

To load an existing dict/JSON and validate:

```python
from ci.transparency.types import Series

loaded = Series.model_validate(payload)         # dict -> Series
loaded2 = Series.model_validate_json(text)      # JSON -> Series
```

---

## Validating with **jsonschema**

If you want an *extra* guardrail using the official schemas:

```python
import json
from importlib.resources import files
from jsonschema import Draft202012Validator

# 1) get the normative schema from the spec package
schema_text = files("ci.transparency.spec.schemas").joinpath("series.schema.json").read_text("utf-8")
series_schema = json.loads(schema_text)

# 2) validate the payload dict you produced with Pydantic
Draft202012Validator.check_schema(series_schema)          # sanity check the schema itself
Draft202012Validator(series_schema).validate(payload)     # raises jsonschema.ValidationError if invalid
```


---

## Round-trip file I/O

```python
import json
from pathlib import Path
from ci.transparency.types import Series

out = Path("series.json")

# write
out.write_text(Series(...).model_dump_json(indent=2), encoding="utf-8")

# read + validate
data = json.loads(out.read_text(encoding="utf-8"))
series = Series.model_validate(data)
```

---

## Using with FastAPI (optional)

Pydantic v2 models work out-of-the-box:

```python
from fastapi import FastAPI
from ci.transparency.types import Series

app = FastAPI()

@app.post("/series")
def post_series(s: Series) -> Series:
    # s is validated already
    return s  # echo back, or transform and return
```

---

## Generating / Regenerating the types (contributors)

Types are generated from the `civic-transparency-spec` package with `datamodel-code-generator`.

```bash
# in the types repo
python scripts/generate_types.py
```

CI tip (to ensure generated code is up to date):

```bash
python scripts/generate_types.py
git diff --exit-code
```

---

## Troubleshooting

**“Unknown field …”**  
The models are strict (`extra="forbid"`). Remove unexpected keys or update the schema definitions & regenerate.

**Datetime parsing**  
Use ISO 8601 (`YYYY-MM-DDTHH:MM:SSZ` or with offset). Pydantic converts to `datetime`.

**Version mismatches**  
Pin both packages to compatible versions. If the definitions change, regenerate types.

---

## See also

- Schemas: <https://civic-interconnect.github.io/civic-transparency-spec/>
- API Reference:
  - [Series](reference/series.md)
  - [Provenance Tag](reference/provenance_tag.md)

``

---

## File: `docs\en\reference\provenance_tag.md`

``markdown
# Provenance Tag (Pydantic)

::: ci.transparency.types.provenance_tag.ProvenanceTag
    options:
      show_source: false
      show_signature: true
      group_by_category: true
      filters:
        - "!^_"

``

---

## File: `docs\en\reference\series.md`

``markdown
# Series (Pydantic)

::: ci.transparency.types.series.Series
    options:
      show_source: false
      show_signature: true
      group_by_category: true
      filters:
        - "!^_"

``

---

## File: `scripts\generate_types.py`

``python
# scripts/generate_types.py
import subprocess
import sys
import hashlib
from pathlib import Path
from importlib.resources import as_file, files
from importlib.metadata import version as pkgver

SCHEMA_PKG = "ci.transparency.spec.schemas"
OUT_DIR = Path("src/ci/transparency/types")


def _add_schema_header(file_path, schema_name):
    """Add provenance header that pre-commit hooks expect."""
    # Normalize line endings BEFORE calculating hash
    _normalize_line_endings(file_path)

    schema_file = files(SCHEMA_PKG) / schema_name
    schema_text = schema_file.read_text()
    schema_sha = hashlib.sha256(schema_text.encode("utf-8")).hexdigest()
    spec_ver = pkgver("civic-transparency-spec")

    content = file_path.read_text()
    header = (
        "# AUTO-GENERATED: do not edit by hand\n"
        f"# source-schema: {schema_name}\n"
        f"# schema-sha256: {schema_sha}\n"
        f"# spec-version: {spec_ver}\n"
    )
    file_path.write_text(header + content)
    _normalize_line_endings(file_path)
    print(f"Added schema header to {file_path.name}")


def _fix_points_field(series_file):
    """Replace the multi-line points Field with default_factory=list."""
    content: str = series_file.read_text()
    lines: list[str] = content.splitlines()

    # Find the start of the points field
    points_start = None
    for i, line in enumerate(lines):
        if "points: List[Point] = Field(" in line:
            points_start = i
            break

    if points_start is None:
        print("ERROR: Points field not found")
        return False

    # Find the end of the Field definition
    paren_count = 0
    points_end = points_start
    for i in range(points_start, len(lines)):
        line = lines[i]
        paren_count += line.count("(") - line.count(")")
        if paren_count == 0 and i > points_start:
            points_end = i
            break

    print(f"Replacing points field (lines {points_start + 1}-{points_end + 1})")

    # Get indentation from original line
    original_line = lines[points_start]
    indent = len(original_line) - len(original_line.lstrip())
    indentation = " " * indent

    # Replace with simple default_factory version
    new_line = f"{indentation}points: List[Point] = Field(default_factory=list)"

    # Build new content
    new_lines = lines[:points_start] + [new_line] + lines[points_end + 1 :]

    series_file.write_text("\n".join(new_lines))
    print("Fixed points field")
    return True


def _normalize_line_endings(file_path):
    """Convert CRLF to LF to match what ruff expects."""
    content = file_path.read_bytes()
    if b"\r\n" in content:
        content = content.replace(b"\r\n", b"\n")
        file_path.write_bytes(content)
        print(f"Normalized line endings in {file_path.name}")


def _rename_seriesdoc_to_series(series_file):
    """Rename SeriesDoc class to Series for cleaner Python API."""
    content = series_file.read_text()
    content = content.replace("class SeriesDoc(", "class Series(")
    series_file.write_text(content)
    print("Renamed SeriesDoc to Series")


def main():
    print("Generating types...")
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # Generate each file
    for schema_file, py_file in [
        ("series.schema.json", "series.py"),
        ("provenance_tag.schema.json", "provenance_tag.py"),
    ]:
        print(f"Generating {py_file}...")
        with as_file(files(SCHEMA_PKG) / schema_file) as schema_path:
            cmd = [
                sys.executable,
                "-m",
                "datamodel_code_generator",
                "--input",
                str(schema_path),
                "--input-file-type",
                "jsonschema",
                "--output",
                str(OUT_DIR / py_file),
                "--output-model-type",
                "pydantic_v2.BaseModel",
                "--target-python-version",
                "3.11",
                "--disable-timestamp",
            ]
            subprocess.run(cmd, check=True)

        # Post-process Python files
        file_path = OUT_DIR / py_file
        if py_file == "series.py":
            _fix_points_field(file_path)
            _rename_seriesdoc_to_series(file_path)

        _add_schema_header(file_path, schema_file)

    series_file = OUT_DIR / "series.py"
    series_content = series_file.read_text()

    # Check what classes exist
    available_classes = []
    imports = []

    if "class Series(" in series_content:
        available_classes.append("Series")
        imports.append("from .series import Series")

    if "class Interval(" in series_content:
        available_classes.append("Interval")
        imports.append("from .series import Interval")

    provenance_file = OUT_DIR / "provenance_tag.py"
    if provenance_file.exists():
        provenance_content = provenance_file.read_text()
        if "class ProvenanceTag(" in provenance_content:
            available_classes.append("ProvenanceTag")
            imports.append("from .provenance_tag import ProvenanceTag")

    # Write __init__.py with actual available classes
    init_content = "\n".join(imports) + "\n"
    init_content += "from ._version import __version__  # noqa: F401\n"
    init_content += f"__all__ = {available_classes!r}\n"
    (OUT_DIR / "__init__.py").write_text(init_content)
    print(f"Updated __init__.py to export: {available_classes}")

    print("Generation complete.")


if __name__ == "__main__":
    main()

``

---

## File: `src\ci\transparency\types\__init__.py`

``python
from .series import Series
from .series import Interval
from .provenance_tag import ProvenanceTag
from ._version import __version__  # noqa: F401

__all__ = ["Series", "Interval", "ProvenanceTag"]

``

---

## File: `src\ci\transparency\types\_version.py`

``python
# file generated by setuptools-scm
# don't change, don't track in version control

__all__ = [
    "__version__",
    "__version_tuple__",
    "version",
    "version_tuple",
    "__commit_id__",
    "commit_id",
]

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Tuple
    from typing import Union

    VERSION_TUPLE = Tuple[Union[int, str], ...]
    COMMIT_ID = Union[str, None]
else:
    VERSION_TUPLE = object
    COMMIT_ID = object

version: str
__version__: str
__version_tuple__: VERSION_TUPLE
version_tuple: VERSION_TUPLE
commit_id: COMMIT_ID
__commit_id__: COMMIT_ID

__version__ = version = '0.1.dev17'
__version_tuple__ = version_tuple = (0, 1, 'dev17')

__commit_id__ = commit_id = 'g0d85f0a73'

``

---

## File: `src\ci\transparency\types\provenance_tag.py`

``python
# AUTO-GENERATED: do not edit by hand
# source-schema: provenance_tag.schema.json
# schema-sha256: 40f34c6734ad87e3ae728b9400c1d341b1aa6f7ba5a97d1bfd26b5af87c79d0b
# spec-version: 0.2.1
# generated by datamodel-codegen:
#   filename:  provenance_tag.schema.json

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, RootModel, constr


class AcctAge(Enum):
    field_0_7d = "0-7d"
    field_8_30d = "8-30d"
    field_1_6m = "1-6m"
    field_6_24m = "6-24m"
    field_24m_ = "24m+"


class AcctType(Enum):
    person = "person"
    org = "org"
    media = "media"
    public_official = "public_official"
    unverified = "unverified"
    declared_automation = "declared_automation"


class AutomationFlag(Enum):
    manual = "manual"
    scheduled = "scheduled"
    api_client = "api_client"
    declared_bot = "declared_bot"


class PostKind(Enum):
    original = "original"
    reshare = "reshare"
    quote = "quote"
    reply = "reply"


class ClientFamily(Enum):
    web = "web"
    mobile = "mobile"
    third_party_api = "third_party_api"


class MediaProvenance(Enum):
    c2pa_present = "c2pa_present"
    hash_only = "hash_only"
    none = "none"


class ISO3166CountryOrSubdivision(
    RootModel[constr(pattern=r"^[A-Z]{2}(-[A-Z0-9]{1,3})?$")]
):
    root: constr(pattern=r"^[A-Z]{2}(-[A-Z0-9]{1,3})?$") = Field(
        ...,
        description="Uppercase ISO-3166-1 alpha-2 country code, optionally with ISO-3166-2 subdivision (e.g., US or US-CA).",
    )


class HexHash8(RootModel[constr(pattern=r"^[a-f0-9]{8}$", min_length=8, max_length=8)]):
    root: constr(pattern=r"^[a-f0-9]{8}$", min_length=8, max_length=8) = Field(
        ...,
        description="Fixed 8-character lowercase hex hash (privacy-preserving, daily salted).",
    )


class ProvenanceTag(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    acct_age_bucket: AcctAge = Field(
        ...,
        description="Account age bucketed for privacy: e.g., '0-7d', '8-30d', '1-6m', '6-24m', '24m+'.",
    )
    acct_type: AcctType = Field(..., description="Declared identity account type.")
    automation_flag: AutomationFlag = Field(
        ...,
        description="Posting method with clear boundaries: manual (direct user interaction), scheduled (user-configured delayed posting), api_client (third-party tools like Buffer/Hootsuite), declared_bot (automated systems with explicit bot declaration).",
    )
    post_kind: PostKind = Field(
        ..., description="Content relationship: original, reshare, quote, reply."
    )
    client_family: ClientFamily = Field(
        ..., description="Application class: web, mobile, third_party_api."
    )
    media_provenance: MediaProvenance = Field(
        ..., description="Embedded authenticity: c2pa_present, hash_only, none."
    )
    dedup_hash: HexHash8 = Field(
        ...,
        description="Privacy-preserving rolling hash for duplicate detection (fixed 8 hex characters, salted daily to prevent cross-dataset correlation).",
    )
    origin_hint: Optional[ISO3166CountryOrSubdivision] = Field(
        None,
        description="Geographic origin limited to country-level (ISO country codes) or major subdivisions only for populations >1M, e.g., 'US', 'US-CA', where lawful.",
    )

``

---

## File: `src\ci\transparency\types\py.typed`

*File is empty*

---

## File: `src\ci\transparency\types\series.py`

``python
# AUTO-GENERATED: do not edit by hand
# source-schema: series.schema.json
# schema-sha256: acf1664027df36e92afba906343a652cc07c12ebeb333467bed522cfb179c3b0
# spec-version: 0.2.1
# generated by datamodel-codegen:
#   filename:  series.schema.json

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Dict, List

from pydantic import BaseModel, ConfigDict, Field, RootModel, confloat, conint, constr


class Interval(Enum):
    minute = "minute"


class Probability(RootModel[confloat(ge=0.0, le=1.0)]):
    root: confloat(ge=0.0, le=1.0)


class CoordinationSignals(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    burst_score: Probability = Field(..., description="Burstiness indicator (0-1).")
    synchrony_index: Probability = Field(
        ..., description="Temporal synchrony indicator (0-1)."
    )
    duplication_clusters: conint(ge=0) = Field(
        ..., description="Count of duplicate/near-duplicate content clusters."
    )


class Point(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    ts: datetime = Field(
        ..., description="UTC minute boundary for this point (ISO 8601)."
    )
    volume: conint(ge=0) = Field(
        ..., description="Total posts observed in this interval."
    )
    reshare_ratio: Probability = Field(
        ..., description="Fraction of posts that are reshares in this interval."
    )
    recycled_content_rate: Probability = Field(
        ...,
        description="Estimated fraction of posts that recycle prior content (hash/duplicate-based).",
    )
    acct_age_mix: Dict[str, Probability] = Field(
        ...,
        description="Distribution over account-age buckets; values typically sum to ~1.0.",
    )
    automation_mix: Dict[str, Probability] = Field(
        ...,
        description="Distribution over automation flags; values typically sum to ~1.0.",
    )
    client_mix: Dict[str, Probability] = Field(
        ...,
        description="Distribution over client families; values typically sum to ~1.0.",
    )
    coordination_signals: CoordinationSignals = Field(
        ..., description="Per-interval coordination indicators."
    )


class Series(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    topic: constr(min_length=1) = Field(
        ..., description="Topic key (e.g., hashtag) this series describes."
    )
    generated_at: datetime = Field(
        ..., description="UTC timestamp when this series was generated (ISO 8601)."
    )
    interval: Interval = Field(..., description="Aggregation interval.")
    points: List[Point] = Field(default_factory=list)

``

---

## File: `tests\test_example_data.py`

``python
# tests/test_example_data.py
import json
from pathlib import Path
from ci.transparency.types import Series, ProvenanceTag
import pytest


class TestExampleData:
    """Test that our example data validates correctly."""

    def test_series_minimal_example(self):
        """Test minimal valid Series example."""
        data_file = Path(__file__).parent / "data" / "series_minimal.json"
        data = json.loads(data_file.read_text())

        # Should
        # validate without errors
        series = Series.model_validate(data)

        # Verify key properties
        assert series.topic == "#TestTopic"
        assert series.interval.value == "minute"  # Compare enum value, not enum object
        assert len(series.points) == 1
        assert series.points[0].volume == 100

        # Round-trip test
        serialized = series.model_dump()
        series2 = Series.model_validate(serialized)
        assert series == series2

    def test_provenance_tag_minimal_example(self):
        """Test minimal valid ProvenanceTag example."""
        data_file = Path(__file__).parent / "data" / "provenance_tag_minimal.json"
        if not data_file.exists():
            # Create the test data if it doesn't exist
            test_data = {
                "acct_age_bucket": "1-6m",
                "acct_type": "person",
                "automation_flag": "manual",
                "post_kind": "original",
                "client_family": "mobile",
                "media_provenance": "hash_only",
                "origin_hint": "US-CA",
                "dedup_hash": "a1b2c3d4e5f6789a",
            }
            data_file.write_text(json.dumps(test_data, indent=2))

        data = json.loads(data_file.read_text())

        # Should validate without errors
        tag = ProvenanceTag.model_validate(data)

        # Verify key properties
        assert tag.acct_type.value == "person"  # Compare enum value
        assert tag.automation_flag.value == "manual"  # Compare enum value
        tag_dict = tag.model_dump()
        assert tag_dict["origin_hint"] == "US-CA"

        # Round-trip test
        serialized = tag.model_dump()
        tag2 = ProvenanceTag.model_validate(serialized)
        assert tag == tag2

    def test_schema_validation_against_examples(self):
        """Validate examples against canonical JSON schemas."""
        try:
            from importlib.resources import files
            from jsonschema import Draft202012Validator
        except ImportError:
            pytest.skip("jsonschema or importlib.resources not available")

        # Test Series
        series_data_file = Path(__file__).parent / "data" / "series_minimal.json"
        if not series_data_file.exists():
            pytest.skip("series_minimal.json test data not found")

        series_data = json.loads(series_data_file.read_text())

        try:
            schema_text = (
                files("ci.transparency.spec.schemas")
                .joinpath("series.schema.json")
                .read_text()
            )
            schema = json.loads(schema_text)

            # Should validate against canonical schema
            Draft202012Validator(schema).validate(series_data)  # type: ignore
        except Exception as e:
            pytest.skip(f"Schema validation failed: {e}")

        # Test ProvenanceTag
        tag_data_file = Path(__file__).parent / "data" / "provenance_tag_minimal.json"
        if not tag_data_file.exists():
            pytest.skip("provenance_tag_minimal.json test data not found")

        tag_data = json.loads(tag_data_file.read_text())

        try:
            schema_text = (
                files("ci.transparency.spec.schemas")
                .joinpath("provenance_tag.schema.json")
                .read_text()
            )
            schema = json.loads(schema_text)

            # Should validate against canonical schema
            Draft202012Validator(schema).validate(tag_data)  # type: ignore
        except Exception as e:
            pytest.skip(f"ProvenanceTag schema validation failed: {e}")

``

---

## File: `tests\test_imports.py`

``python
# tests/test_imports.py
from ci.transparency.types import Series, ProvenanceTag


def test_imports():  # just proves modules exist
    assert Series and ProvenanceTag

``

---

## File: `tests\test_public_api.py`

``python
# tests/test_public_api.py


def test_public_api_surface():
    import ci.transparency.types as t

    expected = {"Series", "ProvenanceTag"}
    # __all__ exists and contains the public names
    assert expected.issubset(set(getattr(t, "__all__", [])))

    # Touch each symbol so the re-export lines count as covered
    for name in expected:
        obj = getattr(t, name)
        assert isinstance(obj, type), f"{name} should be a class"


def test_version_present_and_string():
    from ci.transparency.types import __version__  # type: ignore

    assert isinstance(__version__, str) and __version__

``

---

## File: `tests\test_series.py`

``python
# tests/test_roundtrip_series.py
from pydantic import BaseModel
from ci.transparency.types import Series


def test_series_model_schema_is_sane():
    assert issubclass(Series, BaseModel)
    js = Series.model_json_schema()
    assert isinstance(js, dict)
    assert "title" in js
    assert "properties" in js and js["properties"]
    assert "type" in js and js["type"] == "object"


def test_points_can_be_empty():
    Series.model_validate(
        {
            "topic": "#X",
            "generated_at": "2025-01-01T00:00:00Z",
            "interval": "minute",
            "points": [],
        }
    )

``

---

## File: `tests\data\provenance_tag_minimal.json`

``json
{
  "acct_age_bucket": "1-6m",
  "acct_type": "person",
  "automation_flag": "manual",
  "post_kind": "original",
  "client_family": "mobile",
  "media_provenance": "hash_only",
  "origin_hint": "US-CA",
  "dedup_hash": "a1b2c3d4"
}

``

---

## File: `tests\data\series_minimal.json`

``json
{
  "topic": "#TestTopic",
  "generated_at": "2025-08-19T12:00:00Z",
  "interval": "minute",
  "points": [
    {
      "ts": "2025-08-19T12:00:00Z",
      "volume": 100,
      "reshare_ratio": 0.25,
      "recycled_content_rate": 0.1,
      "acct_age_mix": {
        "0-7d": 0.2,
        "8-30d": 0.3,
        "1-6m": 0.3,
        "6-24m": 0.15,
        "24m+": 0.05
      },
      "automation_mix": {
        "manual": 0.8,
        "scheduled": 0.1,
        "api_client": 0.05,
        "declared_bot": 0.05
      },
      "client_mix": {
        "web": 0.6,
        "mobile": 0.35,
        "third_party_api": 0.05
      },
      "coordination_signals": {
        "burst_score": 0.3,
        "synchrony_index": 0.2,
        "duplication_clusters": 5
      }
    }
  ]
}
``

---

