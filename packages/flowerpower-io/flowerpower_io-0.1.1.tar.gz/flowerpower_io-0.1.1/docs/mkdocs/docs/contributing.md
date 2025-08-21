# Contributing to flowerpower-io

We welcome contributions to `flowerpower-io`! Whether it's reporting a bug, suggesting a new feature, or submitting a pull request, your help is valuable.

## Reporting Issues

If you encounter any bugs, unexpected behavior, or have feature requests, please open an issue on our [GitHub Issues page](https://github.com/flowerpower-io/flowerpower-io/issues).

When reporting an issue, please include:
- A clear and concise description of the problem.
- Steps to reproduce the behavior.
- Expected behavior.
- Actual behavior.
- Your operating system and Python version.
- `flowerpower-io` version.
- Any relevant code snippets or error messages.

## Submitting Pull Requests

We encourage you to contribute code to `flowerpower-io`. To submit a pull request:

1.  **Fork the repository**: Start by forking the `flowerpower-io` repository on GitHub.
2.  **Clone your fork**: Clone your forked repository to your local machine:
    ```bash
    git clone https://github.com/your-username/flowerpower-io.git
    cd flowerpower-io
    ```
3.  **Create a new branch**: Create a new branch for your changes:
    ```bash
    git checkout -b feature/your-feature-name
    # or
    git checkout -b bugfix/your-bug-description
    ```
4.  **Set up your development environment**:
    It is recommended to use `uv` or `pixi` for dependency management.
    ```bash
    # Using uv
    uv venv
    uv pip install -e ".[all]"
    ```
    ```bash
    # Using pixi
    pixi install
    ```
5.  **Make your changes**: Implement your feature or bug fix. Ensure your code adheres to the project's coding style and includes appropriate tests.
6.  **Test your changes**: Run the test suite to ensure your changes haven't introduced any regressions:
    ```bash
    uv run pytest
    # or if using pixi
    pixi run pytest
    ```
7.  **Commit your changes**: Write clear and concise commit messages.
    ```bash
    git commit -m "feat: Add new awesome feature"
    # or
    git commit -m "fix: Resolve critical bug in CSV loader"
    ```
8.  **Push your branch**: Push your changes to your forked repository:
    ```bash
    git push origin feature/your-feature-name
    ```
9.  **Create a Pull Request**: Open a pull request from your forked repository to the `main` branch of the official `flowerpower-io` repository. Provide a detailed description of your changes.

## Development Setup

For local development, ensure you have Python 3.8+ installed.

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/flowerpower-io/flowerpower-io.git
    cd flowerpower-io
    ```
2.  **Install dependencies**:
    ```bash
    # Using uv (recommended)
    uv venv
    uv pip install -e ".[all]"
    ```
    ```bash
    # Using pixi
    pixi install
    ```
3.  **Run tests**:
    ```bash
    uv run pytest
    # or
    pixi run pytest