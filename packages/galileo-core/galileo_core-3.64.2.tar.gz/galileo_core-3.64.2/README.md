# galileo-core

Shared schemas and configuration for Galileo's Python packages.

## Running Tests

This project uses [Poetry](https://python-poetry.org/) for dependency management and [pytest](https://pytest.org/) as the test runner.

To install the test dependencies and run the test suite, use:

```bash
poetry install --with test
poetry run pytest
```

Or you could run:

```bash
inv test
```

- The first command installs all dependencies, including those needed for testing.
- The second command runs the entire test suite in parallel (as configured in `pyproject.toml`).

If you are developing locally and using this package as a dependency in other projects (e.g., the Galileo API), make sure to use the local path override in your `pyproject.toml`:

```toml
galileo-core = { path = "../galileo-core", develop = true }
```
