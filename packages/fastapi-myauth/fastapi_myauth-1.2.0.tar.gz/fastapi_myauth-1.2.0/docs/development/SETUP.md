# 🛠️ Development Setup Guide for FastAPI MyAuth

This guide describes how to set up your local development environment for `FastAPI MyAuth`. Following these steps will ensure you have all the necessary tools and dependencies to contribute to the project.

## 📋 Prerequisites

- Python 3.13 or newer
- `git`

## ⚙️ Setup Steps

### 1. Clone the Repository

First, fork the `fastapi_myauth` repository on GitHub and then clone your fork locally:

```bash
git clone https://github.com/<YOUR_GITHUB_USERNAME>/fastapi_myauth.git
cd fastapi_myauth
```

If you don't plan to contribute code but just want to run the example, you can clone directly:

```bash
git clone https://github.com/symonk/fastapi_myauth.git # Use the original repo if not contributing
cd fastapi_myauth
```

### 2. Create a Virtual Environment

It's highly recommended to use a virtual environment to manage dependencies for your project.

```bash
python -m venv .venv
```

### 3. Activate the Virtual Environment

On macOS/Linux:

```bash
source ./.venv/bin/activate
```

On Windows:

```bash
.venv\Scripts\activate
```

You should see `(.venv)` or similar at the beginning of your terminal prompt, indicating the virtual environment is active.

### 4. Install Dependencies

Install the project dependencies, including development tools:

```bash
pip install -e ".[dev]"
```

The `-e .` installs the package in editable mode, meaning changes to the source code will be reflected without re-installation. `[dev]` installs the development dependencies defined in `pyproject.toml`.

### 5. Install Pre-commit Hooks (Recommended)

`FastAPI MyAuth` uses `pre-commit` hooks to ensure code quality and consistent formatting (`Ruff` and `Black`). It's strongly recommended to install them:

```bash
pre-commit install
```

These hooks will automatically run checks (like linting and formatting) before each commit, helping you catch issues early.

### 6. Database Setup for Development (SQLite Example)

The example application (`fastapi_myauth/test_main.py`) uses SQLite for simplicity. When running tests or the example app, it will create a `database.db` file in your root directory.

To manually create the tables for the example app:

```python
# From the project root, open a Python interpreter
python
```

```python
from fastapi_myauth.test_main import create_db_and_tables # Assuming this function exists in your test_main.py
from fastapi_myauth.test_main import init_db, get_db

create_db_and_tables()

# Initialize default superuser (optional, but useful for testing)
session = next(get_db())
init_db(session)
session.close()

exit()
```

### 7. Running Tests

To run the test suite and check code coverage:

```bash
./scripts/test.sh
```

This script will execute `pytest` and generate a coverage report.

### 8. Running the Example Application

You can run the example `fastapi_myauth/test_main.py` using `uvicorn`:

```bash
uvicorn fastapi_myauth.test_main:app --reload
```

The API documentation will then be available at `http://127.0.0.1:8000/docs`.

### 9. Linting and Formatting Manually

If you don't use `pre-commit` or want to run checks manually:

```bash
ruff check .
ruff format .
```

You're now ready to start developing and contributing to `FastAPI MyAuth`!
