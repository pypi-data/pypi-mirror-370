# AttackIQ Platform API Utilities

⚠️ **BETA / WORK IN PROGRESS** ⚠️

This package provides utility functions for interacting with the AttackIQ Platform API.

## Status

This project is currently in beta and under active development. Features and APIs may change without notice. Feedback and contributions are welcome!

## Installation

```bash
virtualenv venv
source venv/bin/activate
pip install --upgrade aiq-platform-api python-dotenv
```

## Prerequisites
- Python 3.9+
- Valid AttackIQ Platform credentials
- Basic familiarity with API concepts

## Examples

To get started quickly with the example code:

1. Copy the example files to your project:
```bash
cp examples/basic_usage.py your-project/
cp examples/.env.example your-project/.env
```

2. Configure your credentials:
```bash
# Edit .env file with your AttackIQ Platform credentials
vim .env
```

3. Run the example:
```bash
python basic_usage.py
```

## Contributing

We welcome feedback and contributions! For detailed contribution guidelines, please see [CONTRIBUTING.md](CONTRIBUTING.md).

Quick ways to contribute:
- Open issues for bugs or feature requests
- Submit pull requests
- Provide feedback on the API design

## License

MIT License - See LICENSE file for details