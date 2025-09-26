# Contributing to Open Conference URL

## Submitting an issue

### Bug reports

If you are submitting a bug report, please answer the following questions:

- What version of Open Conference URL were you using?
- What were you doing?
- What did you expect to happen?
- What happened instead?

## Contributing code

Pull requests for bug fixes and new features are always welcome. Please be sure
to add or update unit tests as appropriate. Follow the steps below to set up the
repository for contributing.

### Installing project dependencies

You can install all project dependencies via `uv`. This will automatically install a virtualenv for you.

```bash
uv sync
```

### Running unit tests

The project's unit tests are written using and managed under the [nose2][nose2]
Python package. You can run all unit tests via the `nose2` command.

```bash
nose2
```

## Code coverage

The project currently boasts high code coverage across all source files.
Contributions are expected to maintain this high standard. You can view the
current coverage report via the `coverage` command:

```bash
coverage run -m nose2
coverage report
```

If you want to examine which lines are/aren't covered, you can generate and view
a detailed HTML view of the coverage report like so:

```bash
coverage html
open htmlcov/index.html
```

[nose2]: https://docs.nose2.io/en/latest/
