# Contributing to Portable VeraCrypt/TrueCrypt Recovery GUI

Thank you for your interest in contributing.

## Prerequisites

- Python 3.12 or later
- PySide6 6.7 or later (for GUI development)
- Hashcat (for integration testing)

## Setup

```bash
git clone https://github.com/portable-crypt-recovery/portable-crypt-recovery.git
cd portable-crypt-recovery
python -m pip install -e ".[dev]"
```

## Running Tests

```bash
python -m pytest tests/ -x -q
```

Linting:

```bash
python -m ruff check src/ tests/
```

## Code Style

- Line length: 100 characters
- Python 3.12+ features preferred
- All Hashcat subprocess calls must use `list` args, never `shell=True`
- All workspace paths must be validated as workspace-relative before use
- Never use system temp folders for recovery data
- Never log passwords or keyfile contents

## Pull Request Guidelines

1. Open an issue to discuss significant changes before submitting a PR.
2. Write tests for new functionality.
3. Ensure all existing tests pass before submitting.
4. Follow the existing code style.
5. Update CHANGELOG.md with a summary of your changes.
6. Do not commit generated files, build artifacts, or workspace data.

## Security

See [SECURITY.md](SECURITY.md) for how to report security vulnerabilities.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
