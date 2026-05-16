# Contributing to Temporal Gradient

Thanks for your interest. This project is small, opinionated, and built
around a specific mathematical model. Contributions are welcome — please
read this short guide before opening a PR.

## What's in scope

- New salience scorers (novelty or value implementations behind the
  existing interfaces in [`temporal_gradient/contracts/`](temporal_gradient/contracts/))
- Adapters for real event sources (queue consumers, log tailers, webhook
  receivers) — likely as separate examples rather than core
- Persistence backends for the memory store
- Performance work, additional test coverage, documentation improvements
- Bug fixes (with a failing test that demonstrates the bug)

## What's out of scope

- Claims about cognition, consciousness, or subjective time experience
  — see [`docs/safety.md`](docs/safety.md). The framework is dynamics,
  not theory of mind.
- Renaming or restructuring core state variables (Ψ, τ, S) — these are
  intentionally fixed and load-bearing across docs.
- Breaking changes to the telemetry packet schema without a SCHEMA_VERSION
  bump and a migration note.

## Before you open a PR

1. **Run the tests.** `pytest` should pass on Python 3.10, 3.11, and 3.12.
2. **Add a test** for any behavioral change. The test suite is the
   contract — see [`tests/`](tests/) for style.
3. **Keep the diff focused.** One concern per PR. Refactors separate from
   features separate from fixes.
4. **Update docs** if you change a public interface or default. The
   architecture diagram and packet schema in [`docs/architecture.md`](docs/architecture.md)
   must stay in sync with the code.

## Development setup

```bash
git clone https://github.com/WhatsYourWhy/The-Temporal-Gradient
cd The-Temporal-Gradient
pip install -e ".[dev]"
pytest
```

## Filing an issue

Use the provided templates. For bugs, include:
- Python version
- Minimal reproduction
- Expected vs. actual behavior

For features, lead with the use case, not the implementation. "I need
to do X and the current API forces Y" is more useful than "please add
method Z."

## Style

- No new runtime dependencies without discussion. The core package is
  zero-dependency by design.
- Standard `black`-compatible formatting. No enforced linter, but match
  the surrounding code.
- Type hints on new public functions.
- Comments only when the *why* is non-obvious. Don't narrate the *what*.

## License

By contributing, you agree your contributions are licensed under the
project's [MIT license](LICENSE).
