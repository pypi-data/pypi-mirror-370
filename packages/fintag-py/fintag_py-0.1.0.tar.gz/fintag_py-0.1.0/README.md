# Fintag SDK for Python

This is a Python SDK for interacting with the Fintag API.

## Installation

You can install the SDK using pip:

```bash
pip install fintag-py
```

## Usage

Here's a quick example of how to use the SDK:

```python
from fintag import FintagClient

client = FintagClient(api_key="your_api_key")


# Verify FinTag
fintag_exists = client.verify("fintag_id")
print(fintag_exists)

# Get wallet information
wallet_info = client.get_wallet_info()
print(wallet_info)
```

## Contributing

We welcome contributions! Please see the [CONTRIBUTING.md](CONTRIBUTING.md) file for more information.

## License

This project is licensed under the Apache License, Version 2.0 - see the [LICENSE](LICENSE) file for details.