# baresquare-sdk

[![image](https://img.shields.io/pypi/v/baresquare-sdk.svg)](https://pypi.python.org/pypi/baresquare-sdk)
[![Python versions](https://img.shields.io/badge/python-3.12+-blue.svg)](https://pypi.org/project/baresquare-sdk/)
[![Actions status](https://github.com/BareSquare/sdk-python/workflows/Tests/badge.svg)](https://github.com/BareSquare/sdk-python/actions)

> [!CAUTION]
> This code is published publicly in PyPI - make sure you do not include proprietary information.

Python SDK providing core utilities and cloud provider integrations for Baresquare services.

## Documentation

- **[User Guide](docs/users.md)** - Installation and usage examples
- **[Developer Guide](docs/devs.md)** - Setup, development, and publishing

## Design Decisions

- **Single-package approach**: One `pyproject.toml` with unified versioning across all modules
- **Optional dependencies**: Users install only what they need via extras (base, AWS, development)
- **Modular imports**: Clear separation between core utilities and cloud provider integrations
- **PyPI publishing**: Publicly available package with automated CI/CD via GitHub Actions

## License

MIT License