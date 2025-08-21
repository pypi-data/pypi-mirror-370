# 🤝 Contributing to FastAPI MyAuth

We welcome contributions to `FastAPI MyAuth`! Whether you're fixing a bug, adding a new feature, improving documentation, or just providing feedback, your help is valuable.

Please take a moment to review this document to make the contribution process as smooth as possible.

## 🎯 How to Contribute

1.  **Report Bugs**: If you find a bug, please open an issue on the [GitHub repository](https://github.com/<YOUR_GITHUB_USERNAME>/fastapi_myauth/issues). Provide a clear description, steps to reproduce, and any relevant error messages.
2.  **Suggest Features**: Have an idea for a new feature? Open an issue to discuss it. We appreciate well-thought-out proposals that align with the project's goals.
3.  **Improve Documentation**: Spotted a typo, an unclear explanation, or something missing? Please submit a pull request with your improvements or open an issue.
4.  **Submit Code**: If you want to contribute code (bug fixes, new features), please follow the steps below.

## 🛠️ Setting up Your Development Environment

For detailed instructions on setting up your local environment, please refer to the [Development Setup Guide](SETUP.md).

## 🚀 Workflow for Code Contributions

1.  **Fork the Repository**: Start by forking the `fastapi_myauth` repository on GitHub.
2.  **Clone Your Fork**: Clone your forked repository to your local machine:
    ```bash
    git clone https://github.com/<YOUR_GITHUB_USERNAME>/fastapi_myauth.git
    cd fastapi_myauth
    ```
3.  **Create a New Branch**: Always create a new branch for your work. Use a descriptive name like `feature/your-feature-name` or `bugfix/issue-number`.
    ```bash
    git checkout -b feature/your-awesome-feature
    ```
4.  **Make Your Changes**: Implement your changes.
    - Ensure your code adheres to the existing coding style and conventions (see "Coding Style" below).
    - Add or update tests to cover your changes.
    - Update documentation if your changes affect public APIs or behavior.
5.  **Run Tests**: Before committing, make sure all tests pass and your changes haven't introduced any regressions.
    ```bash
    ./scripts/test.sh
    ```
6.  **Run Linters/Formatters**: Ensure your code is formatted and linted correctly.
    ```bash
    pre-commit run --all-files
    ```
7.  **Commit Your Changes**: Write clear and concise commit messages. Follow the [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) specification if possible (e.g., `feat: add new login method`, `fix: resolve password reset bug`). This helps with automated release management.
    ```bash
    git commit -m "feat: implement new awesome feature"
    ```
8.  **Push to Your Fork**: Push your branch to your forked repository on GitHub.
    ```bash
    git push origin feature/your-awesome-feature
    ```
9.  **Open a Pull Request (PR)**:
    - Go to your forked repository on GitHub.
    - Click on "New Pull Request" (or similar button).
    - Ensure your branch is selected.
    - Provide a clear and detailed description of your changes in the PR description template. Link to any relevant issues.
    - Submit the PR.

## 📏 Coding Style

This project uses `Ruff` for linting and `Black` (via Ruff's `E501` ignore and `pre-commit` hook) for code formatting.

- **Ruff**: We use `ruff` to enforce code quality and style. Please run it before committing.
- **Black**: Files are formatted with `Black`. `pre-commit` hooks are configured to run `Black` automatically.

To ensure your code adheres to the style, we recommend setting up [pre-commit hooks](https://pre-commit.com/):

```bash
pip install pre-commit
pre-commit install
```

This will automatically run `ruff` (and `Black` implicitly) and other checks before you commit.

## 🧪 Testing

- All new features and bug fixes should be accompanied by appropriate unit or integration tests.
- Tests are written using `pytest`.
- Run tests using the provided script: `./scripts/test.sh`. This also generates a coverage report.

## ⚠️ Code of Conduct

Please note that this project is released with a [Code of Conduct](CODE_OF_CONDUCT.md). By participating in this project, you agree to abide by its terms.

Thank you for contributing!
