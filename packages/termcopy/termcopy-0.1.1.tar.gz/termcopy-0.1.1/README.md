# termcopy

[![CI](https://github.com/scaryPonens/termco-py/actions/workflows/test.yml/badge.svg)](https://github.com/scaryPonens/termco-py/actions/workflows/test.yml)

A Python CLI tool for terminal clipboard operations, replicating the functionality of a bash script that sends OSC 52 escape sequences.

## Installation

```bash
pip install termcopy
```

## Usage

The tool reads input from either a file or stdin, base64 encodes it, and outputs an OSC 52 escape sequence for clipboard operations.

### From a file:
```bash
termcopy filename.txt
```

### From stdin:
```bash
echo "Hello, World!" | termcopy
```

### From a pipe:
```bash
cat somefile.txt | termcopy
```

## How it works

The tool:
1. Detects whether input is coming from a terminal or pipe
2. Reads from a file argument if input is from terminal, otherwise reads from stdin
3. Base64 encodes the input data
4. Removes newlines from the base64 output
5. Wraps the result in an OSC 52 escape sequence for clipboard operations

## Development

To install in development mode:

```bash
pip install -e .
```

To install with development dependencies:

```bash
pip install -e ".[dev]"
```

### Running tests

```bash
pytest tests/ -v
```

### Code formatting and linting

```bash
# Format code
black src/ tests/

# Check code style
flake8 src/ tests/

# Type checking
mypy src/
```

## CI/CD

This project uses GitHub Actions for continuous integration and deployment:

- **Test workflow** (`.github/workflows/test.yml`): Runs on every push and pull request
  - Tests against Python 3.8-3.12
  - Runs linting (black, flake8, mypy)
  - Uploads coverage reports

- **Publish workflow** (`.github/workflows/publish.yml`): Runs on version tags
  - Builds and publishes to PyPI
  - Also publishes to TestPyPI

- **Manual release workflow** (`.github/workflows/release.yml`): Can be triggered manually
  - Allows custom version releases
  - Optional publishing to PyPI/TestPyPI

### Setting up PyPI publishing

1. Create API tokens on [PyPI](https://pypi.org/manage/account/token/) and [TestPyPI](https://test.pypi.org/manage/account/token/)
2. Add the tokens as GitHub secrets:
   - `PYPI_API_TOKEN`: Your PyPI API token
   - `TEST_PYPI_API_TOKEN`: Your TestPyPI API token

## License

MIT License - see LICENSE file for details.
