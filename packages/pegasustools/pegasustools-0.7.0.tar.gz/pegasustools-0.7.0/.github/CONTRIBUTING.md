See the [Scientific Python Developer Guide][spc-dev-intro] for a detailed
description of best practices for developing scientific packages.

[spc-dev-intro]: https://learn.scientific-python.org/development/

# Quick development

The fastest way to start with development is to use nox. If you don't have nox,
you can use `uvx nox` (or `pipx run nox`) to run it without installing, or
`uvx install nox` (or `pipx install nox`). If you don't have uv or pipx (pip for
applications), then you can install uv with
[this guide](https://docs.astral.sh/uv/getting-started/installation/) and pipx
by running `pip install pipx` (the only case were installing an application with
regular pip is reasonable). If you use macOS, then pipx and nox are both in
brew, use `brew install pipx nox`.

To use, run `nox`. This will lint and test using every installed version of
Python on your system, skipping ones that are not installed. You can also run
specific jobs:

```console
$ nox -s lint  # Lint only
$ nox -s tests  # Python tests
$ nox -s docs  # Build and serve the docs
$ nox -s build  # Make an SDist and wheel
```

Nox handles everything for you, including setting up an temporary virtual
environment for each run.

# Adding Something New

Adding a new function/class/etc is reasonably simple.

1. Either create a new file in `src/pegasustools` or open an existing file.
2. Add the new function/class/etc to the file.
3. Open `src/pegasustools/__init__.py`, import the new function/class/etc and
   add it to the `__all__` variable, see the existing examples in the
   `__init__.py` file for details.
4. Write tests for your new code
5. Write documentation for you new code. Documentation is in the `docs`
   directory, see the existing contents of that directory for how to do it.
6. Run the linters and tests using Nox
7. Create a Pull Request (PR) in GitHub
8. Once the PR is merged you can trigger a new release/version by creating a new
   release on GitHub, the GitHub actions will take care of packaging and
   releasing your code.

# Setting up a development environment manually

You can set up a development environment by running:

```bash
python3 -m venv .venv
source ./.venv/bin/activate
pip install -v -e .[dev]
```

If you have the
[Python Launcher for Unix](https://github.com/brettcannon/python-launcher), you
can instead do:

```bash
py -m venv .venv
py -m install -v -e .[dev]
```

# Pre-commit

You should prepare pre-commit, which will help you by checking that commits pass
required checks:

```bash
pip install pre-commit # or brew install pre-commit on macOS
pre-commit install # Will install a pre-commit hook into the git repo
```

You can also/alternatively run `pre-commit run` (changes only) or
`pre-commit run --all-files` to check even without installing the hook.

# Testing

Use pytest to run the unit checks:

```bash
pytest
```

# Building docs

You can build and serve the docs using:

```bash
nox -s docs
```

You can build the docs only with:

```bash
nox -s docs --non-interactive
```
