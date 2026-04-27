# Contributing to Qualichat

Thanks for taking the time to contribute. Qualichat is an open-source
linguistic ethnography tool used by humanities researchers; small,
focused improvements are very welcome.

## Quick links

- [Issue tracker](https://github.com/qualichat/qualichat/issues)
- [Pull requests](https://github.com/qualichat/qualichat/pulls)
- [Changelog](CHANGELOG.md)
- [Documentation](https://qualichat.readthedocs.io)

## Reporting bugs

Open an issue with:

1. **What you ran** — the exact command(s).
2. **What you expected** — and what actually happened.
3. **A minimal example** — ideally a small `.txt` snippet that reproduces
   the problem (anonymised — see *Privacy*, below).
4. **Your environment** — OS, Python version (`python --version`),
   Qualichat version (`python -m qualichat -v`).

## Suggesting features

Open an issue describing the **research question** the feature would
help answer. Qualichat is a research tool, not a general chat analyser;
features that connect cleanly to the project's framing-of-public-opinion
methodology are easier to land than generic chat-stat ideas.

## Setting up a development environment

Requires Python 3.9+ and (on Windows) Visual Studio C++ Build Tools for
the native dependencies (`wordcloud`, `pandas`).

```sh
git clone https://github.com/qualichat/qualichat
cd qualichat

python -m venv .venv
# Linux / macOS:
source .venv/bin/activate
# Windows:
.venv\Scripts\activate

pip install -e ".[dev]"

# Set up the pre-commit hooks (runs ruff on every commit).
pre-commit install
```

Run the test suite:

```sh
pytest                       # all tests
pytest --cov=qualichat       # with coverage
pytest tests/test_chat.py    # one file
pytest -k zip                # by keyword
```

## Code style

The project uses **[ruff](https://docs.astral.sh/ruff/)** for both
linting and formatting (configured in `pyproject.toml`). Run before
opening a PR:

```sh
ruff check .                  # lint
ruff check . --fix            # auto-fix safe issues
ruff format .                 # format
```

If you installed pre-commit, these run automatically on `git commit`.

We use **[mypy](https://mypy.readthedocs.io/)** for type checking, but
strictness is being tightened module by module — start by not making
the *current* state worse.

```sh
mypy qualichat
```

## Pull request guidelines

- **Branch from `main`.** For changes that depend on another open PR,
  branch from that PR's branch and clearly mark the dependency in the
  PR description ("stacked on #N").
- **Conventional commit messages** (`feat:`, `fix:`, `chore:`, `docs:`,
  `test:`, `refactor:`) — the recent history of this repo follows this
  pattern.
- **Tests for new behaviour.** New chart logic, parser quirks, or
  helpers should come with at least one `tests/` case.
- **CHANGELOG entry** under the appropriate version heading. Keep the
  *what* and the *why* — readers want to understand the change without
  diffing.
- **Small PRs over large.** A reviewer can approve a clean 100-line
  change in minutes; a 1000-line change might sit for weeks.

## Privacy and ethics

WhatsApp chat exports contain real, identifiable conversations. When
contributing fixtures, sample exports or screenshots:

- **Synthesise the content** (fictional names, fabricated messages) or
  **anonymise heavily** (see `tests/fixtures/` for examples).
- **Never commit a real export** to this repo, an issue or a PR.
- The bundled anonymisation in `qualichat.utils.get_random_name` maps
  contact names to pseudonyms — but the mapping is stored in
  `~/.qualichat/config.json`. Treat that file as private.
- For research uses, follow your institution's ethics-committee
  guidelines and the LGPD / GDPR. Notify chat participants before
  analysing groups they are members of.

## Questions

Open a discussion or an issue. The maintainers prefer asynchronous
written conversation over synchronous chat.
