# Contributing to Nebula-Writer

Thank you for your interest in contributing! Nebula-Writer is an AI-powered fiction writing assistant.

## Development Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/sagar0163/Nebula-Writer.git
   cd Nebula-Writer
   ```

2. **Set up a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install -e .
   ```

4. **Install pre-commit hooks**:
   ```bash
   pre-commit install
   ```

## Code Quality

We use the following tools to maintain code quality:

- **Ruff**: For linting and formatting.
- **Pytest**: For testing.
- **Black**: For additional formatting (enforced by Ruff).

Run linting locally:
```bash
ruff check .
ruff format .
```

Run tests:
```bash
pytest
```

## Pull Request Process

1. Create a new branch for your feature or bugfix.
2. Ensure all tests pass and linting is clean.
3. Submit a PR with a clear description of changes.

---
*Made with love by the Nebula-Writer team.*
