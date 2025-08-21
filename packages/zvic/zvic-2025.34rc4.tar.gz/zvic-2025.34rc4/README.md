[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE) [![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/)

# ZVIC

***ZVIC: Runtime interface compatibility for Python modules—no version numbers required.***

Zero-Version Interface Contracts (ZVIC) is both a project and a paradigm for signature-based compatibility in Python modules. ZVIC enables safe, dynamic code reuse and interface stability without version numbers, using runtime verification of callable structure.

License: MIT — see the `LICENSE` file for details (SPDX: MIT).

## Key Concepts

- **Zero-Version Interface Contracts (ZVIC):** Manages code compatibility without version numbers, relying on signature hashes and runtime checks. Contracts are verified at definition time and dynamically at runtime.

## Who Should Use ZVIC?

- Library authors who want to guarantee interface compatibility without versioning headaches.
- Teams practicing hot-reload or rapid deployment of Python modules.
- Anyone needing robust, runtime-checked API contracts for Python code.

## Goals

- Eliminate the need for semantic versioning in shared code
- Enable safe, hot-reloadable modules
- Provide runtime guarantees for interface compatibility
- Facilitate rapid development and deployment cycles

## Installation & requirements

- Requirements:
	- Python 3.12+

- Install (user):

	```sh
	pip install zvic
	```

- Install (developer / editable):

	1. Create and activate a virtual environment

		 - Windows (PowerShell):

			 ```powershell
			 py -3.12 -m venv .venv
			 .\.venv\Scripts\Activate.ps1
			 ```

		 - Unix / macOS:

			 ```sh
			 python3 -m venv .venv
			 source .venv/bin/activate
			 ```

	2. Install the package in editable mode:

		 ```sh
		 pip install -e .
		 ```

	If you want CrossHair support for semantic constraint analysis (optional), install the extra:

	```sh
	pip install .[crosshair]
	```

### Quickstart
For a minimal programmatic check you can use the following snippet (run from the repo root):

```py
from pathlib import Path
from zvic import load_module
from zvic.compatibility import is_compatible
from zvic.exception import SignatureIncompatible

a = load_module(Path('tests/stuff/mod_a.py'), 'mod_a')
b = load_module(Path('tests/stuff/mod_b.py'), 'mod_b')

try:
	is_compatible(a.P2, b.P2)
	print('compatible')
except SignatureIncompatible as e:
	print('incompatible:')
	print(e.to_json())
```


## Canonicalization & Compatibility

Function signatures are canonicalized to ensure consistent interface identification and compatibility checks. See the [Canonicalization & Compatibility Spec](docs/specs/spec-04-Canonicalization-Compatibility.md) for details and compatibility rules.

## Compatibility testing levels
ZVIC tests compatibility at multiple levels to give consumers high confidence before accepting a new module or version. The test strategy is deliberate and layered so that regressions are caught early and explained clearly.

- Public interface presence
	- Modules are compared by their public attributes (respecting `__all__` when present). Any public attribute present in A but missing from B is reported as an incompatibility.

- Callable-level checks (structural)
	- Callables (functions, methods, class `__call__`) are checked for signature compatibility. This covers parameter kinds (positional-only, positional-or-keyword, keyword-only), `*args`/`**kwargs`, default values, and parameter names where appropriate.
	- `are_params_compatible()` implements the scenario-based rules from the spec and raises structured errors when B cannot accept all calls that A accepts.

- Type normalization and compatibility
	- A type-normalization layer canonicalizes runtime annotation types to a uniform schema.
	- `is_type_compatible()` implements rules such as: exact-type equality, allowed widening (derived→base contravariant acceptance), disallowed narrowing (base→derived), container invariance for invariants (e.g., `list[int]`), and ABC-aware acceptance.

- Constraint checks (Annotated)
- Constraint checking (Annotated)
	- ZVIC recognizes `typing.Annotated[T, constraint]` forms and will transform inline call-style annotations into `Annotated[...]` during module loading when necessary.
	- Constraint checking is best-effort: if the optional CrossHair analyser is installed, ZVIC will attempt a semantic verification (searching for counterexamples). If CrossHair is not available or cannot analyze a predicate, ZVIC falls back to deterministic heuristics (for example numeric/length comparisons) and ultimately to exact-match of the constraint expression.

- Class and enum checks
	- Classes are compared for missing methods, and important special call sites such as `__init__` and `__call__` are compared recursively.
	- Enum compatibility ensures member presence and value stability (we require that names present in A also exist in B and that their underlying values remain equal), while allowing reordering or new additional members in B.

- End-to-end tests
	- The test-suite includes unit tests that exercise canonicalization, parameter scenarios, type compatibility edge-cases, and small integration examples. See `tests/` for examples and `docs/specs/spec-08-Test-Plan.md` for the test plan.

## How to run the test-suite

From the repository root:

```sh
pytest -q
```

Run a single test file (example):

```sh
pytest tests/test_spec08_compatibility.py -q
```

Optional: run an individual test by name with `-k`.

## Constraint checking and security - BEWARE MAGIC
Take this example:

	def foo(x: int(_ < 10)) -> int(_ < 10):
		return x * 2

Note that the `_ < 10` must be a valid Python expression (and thus is valid Python syntax, even though it looks weird!), but it is not evaluated in this context. With `from __future__ import annotations`, the whole annotation is treated as a string. ZVIC extracts this part and transforms it - first we append it to the docstring as pre/post conditions for crosshair to analyze "statically", second we transform the expression into a valid `assert` for runtime checking, if the interpreter is running in debug (not-optimized) mode.

If CrossHair is present, ZVIC will try to use it to search for counterexamples; if CrossHair is not present or cannot handle the predicate, ZVIC uses deterministic heuristics (numeric/length comparisons) and finally requires an exact expression match as a last resort.

## Security note
ZVIC performs runtime annotation resolution and, in some code paths, evaluates constraint expressions. This can execute arbitrary code from the loaded module. ***Do not run ZVIC against untrusted code without an appropriate sandbox***. If you must inspect untrusted modules, consider running ZVIC in an isolated environment (container, VM, or restricted subprocess). Since ZVIC also makes use of eval() to check type compatibility in dynamic contexts, be aware that this can execute arbitrary code from the module being checked even if you don't make use of constraints - **exercise caution**.

## Runtime requirements and packaging
- Python: 3.12+
- Install locally (editable):

```sh
pip install -e .
```

## Release notes and changelog
See `CHANGELOG.md` for release history and the summary of specs implemented in each release.

## Examples (from spec-08 tests)

Below are small, representative examples taken from the `spec-08` compatibility tests in `tests/stuff/` with the expected ZVIC behaviour.

- Compatible example (P1): positional-only parameters, same required/total — compatible, different names

```py
# Module A
def P1(a, b, /):
	pass

# Module B
def P1(x, y, /):
	pass

# Expected: is_compatible(mod_a.P1, mod_b.P1) -> no exception (compatible)
```

- Incompatible example (P2): B adds a required parameter — incompatible

```py
# Module A
def P2(a, b, /):
	pass

# Module B
def P2(x, y, z, /):
	pass

# Expected: is_compatible(mod_a.P2, mod_b.P2) -> raises SignatureIncompatible
# Typical diagnostic (ZVIC will raise `SignatureIncompatible` with context):
# {
#   "message": "B has more required parameters than A",
#   "context": {"A": "(a, b, /)", "B": "(x, y, z, /)"},
#   "error_id": "ZV1001",
# }
```

- Constraint narrowing example (C4): A permits values < 20, B restricts to < 10 — incompatible

```py
# Module A
def C4(a: int(_ < 20)):
	pass

# Module B
def C4(a: int(_ < 10)):
	pass

# Expected: is_compatible(mod_a.C4, mod_b.C4) -> raises SignatureIncompatible
# Typical diagnostic message string produced by ZVIC:
# "Constraint mismatch for parameter a: _ < 20 vs _ < 10 (B is narrower and thus incompatible: some inputs that A accepts will not be accepted by B)"
```

## Try the examples

You can run a small convenience script that loads the real `tests/stuff` modules and prints compatibility results for a few spec-08 scenarios.

From the repository root (PowerShell example):

```powershell
py -3.12 examples/run_spec08_examples.py
```

Or, if your default python interpreter is Python >= 3.12 and on PATH:

```sh
py examples/run_spec08_examples.py
```

Sample output (trimmed):

--- Example: P1 ---
Result: compatible (no exception)

--- Example: P2 ---
Result: incompatible — diagnostic:
{
	"error_id": "ZV1001",
	"type": "SignatureIncompatible",
	"severity": "error",
	"message": "B has more required parameters than A",
	"context": {"A": "(a, b, /)", "B": "(x, y, z, /)", "llm_hint": "..."},
	...
}

--- Example: C4 ---
Result: incompatible — diagnostic:
{
	"error_id": "ZV1001",
	"type": "SignatureIncompatible",
	"severity": "error",
	"message": "Constraint mismatch for parameter a: _ < 20 vs _ < 10 (B is narrower and thus incompatible: some inputs that A accepts will not be accepted by B)",
	...
}

## Project status

Stability: Beta

- Development status: actively developed and maintained. The test-suite runs locally and the repository currently has a comprehensive unit test suite, with all tests passing.
- Test coverage: unit tests exercise canonicalization, compatibility scenarios, and edge-cases.
- API stability: not guaranteed. Public APIs may change between releases as the project iterates on the specification and compatibility rules — please pin versions for production use and run the test-suite when upgrading.
- Recommended use: evaluation, experimentation, and integration testing. For critical production use, perform an acceptance pass and pin a released version.
- Contributing: contributions, issues, and PRs are welcome; see `CHANGELOG.md` and the `docs/specs/` for the current design decisions.

## Project Structure
- `README.md` - this document
- `src/` - Main source code
- `tests/` - Test suite (unit, integration, TDD, quick tests)
- `docs/specs/` - Detailed specifications
- `pyproject.toml` - Build and packaging configuration
- `setup.py` - Minimal legacy packaging script
- `CHANGELOG.md` - Release notes and change history
- `examples/` - Example scripts and usage patterns

## Further Reading

- [Spec 01: Introduction](docs/specs/spec-01-Introduction.md)
- [Spec 02: SDFP Principles](docs/specs/spec-02-SDFP-Principles.md)
- [Spec 03: ZVIC Contracts](docs/specs/spec-03-ZVIC-Contracts.md)
- [Spec 04: Canonicalization & Compatibility](docs/specs/spec-04-Canonicalization-Compatibility.md)

## Versioning Scheme

ZVIC uses a CalVer versioning scheme: `YYYY.0W[.patchN/devN/rcN]`, where:
- `YYYY` is the year
- `0W` is the zero-padded ISO week number
- Optional `.patchN`, `.devN`, `.rcN` for patches, dev, or release candidates

For example, `2025.26` corresponds to week 26 of 2025. This mirrors the structure of our Scrum logs (see `/docs/scrum/README.md`).

# Office Hours
You can also contact me one-on-one! Check my [office hours](https://calendly.com/amogorkon/officehours) to set up a meeting :-)

If you have questions also feel free to use the github issues or the [ZVIC Discussions](https://github.com/amogorkon/ZVIC/discussions).


***Enjoy!***