# Galtea SDK

<p align="center">
  <img src="https://galtea.ai/img/galtea_mod.png" alt="Galtea" width="500" height="auto"/>
</p>

<p align="center">
  <strong>Comprehensive AI/LLM Testing & Evaluation Framework</strong>
</p>

<p align="center">
	<a href="https://pypi.org/project/galtea/">
		<img src="https://img.shields.io/pypi/v/galtea.svg" alt="PyPI version">
	</a>
	<a href="https://pypi.org/project/galtea/">
		<img src="https://img.shields.io/pypi/pyversions/galtea.svg" alt="Python versions">
	</a>
	<a href="https://www.apache.org/licenses/LICENSE-2.0">
		<img src="https://img.shields.io/badge/License-Apache%202.0-blue.svg" alt="License">
	</a>
</p>

## Overview

Galtea SDK empowers AI engineers, ML engineers and data scientists to rigorously test and evaluate their AI products. With a focus on reliability and transparency, Galtea offers:

1. **Automated Test Dataset Generation** - Create comprehensive test datasets tailored to your AI product
2. **Sophisticated Product Evaluation** - Evaluate your AI products across multiple dimensions

## Documentation

**All SDK usage and API documentation has moved to our official docs:** [Galtea SDK Documentation](https://docs.galtea.ai/sdk/introduction)

---

## Development

This project uses Poetry for dependency management and packaging.

### Development Setup

```bash
# Print the command to activate the virtual environment
poetry env activate

# Activate the virtual environment by copy-pasting the command
# Example: C:\Users\user\AppData\Local\pypoetry\Cache\virtualenvs\galtea-MmpOHh8e-py3.12\Scripts\activate.ps1

# Install dependencies
poetry install
```

> Exit the virtual environment with `exit` command.

### Running Tests

Tests are located in the `tests/` directory. To run all tests:

```bash
poetry run pytest
```

### Building the Project

To build the project:

```bash
poetry build
```

This will create distribution packages (wheel and source distribution) in the `dist/` directory.

## License

Apache License 2.0
