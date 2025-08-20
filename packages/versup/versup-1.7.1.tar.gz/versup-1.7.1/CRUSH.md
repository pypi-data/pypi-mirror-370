# Build/Test Commands
make test                    # Run all tests with coverage
pytest src/tests/test_name.py  # Run specific test file
ruff check src/versup       # Lint with ruff (preferred)
flake8 src/versup           # Alternative lint
mypy src/versup --ignore-missing-imports  # Type check
pip install -e .             # Build and install package

# Code Style
- Use double quotes for strings
- Line length: 88 characters (E501 ignored)
- Imports: Prefer relative imports within versup package
- Type hints required for all function parameters and returns
- Use VersupError for all custom exceptions (not generic Exception)
- Prefer semver for version handling
- Use Rich library for console output
- Test files: src/tests/test_name.py