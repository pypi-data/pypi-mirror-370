# Contributing to Metis Agent

Thank you for your interest in contributing to Metis Agent! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Environment](#development-environment)
- [Coding Standards](#coding-standards)
- [Pull Request Process](#pull-request-process)
- [Testing](#testing)
- [Documentation](#documentation)
- [Issue Reporting](#issue-reporting)
- [Feature Requests](#feature-requests)

## Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct. Please be respectful and considerate of others.

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally
3. Set up the development environment
4. Create a branch for your changes
5. Make your changes
6. Test your changes
7. Submit a pull request

## Development Environment

### Prerequisites

- Python 3.8 or higher
- pip
- virtualenv or conda (recommended)

### Setup

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

3. Set up pre-commit hooks:
   ```bash
   pre-commit install
   ```

## Coding Standards

We follow these coding standards:

- **PEP 8**: For Python code style
- **Type Hints**: Use type hints for function parameters and return values
- **Docstrings**: Use Google-style docstrings
- **Imports**: Sort imports using isort
- **Formatting**: Format code using Black

Run the following commands to check your code:

```bash
# Format code
black metis_agent
isort metis_agent

# Check for errors
flake8 metis_agent
mypy metis_agent
```

## Pull Request Process

1. Create a new branch for your feature or bugfix:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes and commit them with descriptive commit messages:
   ```bash
   git commit -m "Add feature: your feature description"
   ```

3. Push your branch to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

4. Submit a pull request to the main repository

5. Address any feedback from reviewers

6. Once approved, your pull request will be merged

## Testing

Write tests for all new features and bug fixes. Run the test suite before submitting a pull request:

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=metis_agent

# Run specific tests
pytest metis_agent/test_system.py
```

## Documentation

Update documentation for any changes you make:

- Update docstrings for modified functions and classes
- Update README.md if necessary
- Update DOCUMENTATION.md for significant changes
- Add examples for new features

## Issue Reporting

When reporting issues, please include:

- A clear and descriptive title
- Steps to reproduce the issue
- Expected behavior
- Actual behavior
- Environment information (OS, Python version, package versions)
- Any relevant logs or error messages

## Feature Requests

For feature requests, please include:

- A clear and descriptive title
- A detailed description of the proposed feature
- Any relevant examples or use cases
- If possible, a rough implementation plan

Thank you for contributing to Metis Agent!