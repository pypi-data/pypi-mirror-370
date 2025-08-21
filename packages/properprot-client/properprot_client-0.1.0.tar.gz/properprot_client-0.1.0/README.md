# ProperProt Client

`properprot-client` is a Python library for interacting with the ProperProt API.
It provides a simple interface to send requests and handle responses from ProperProt.

## Installation

```bash
pip install properprot-client
```

## Usage
```python
from properprot_client import APIClient

client = APIClient(api_key="API_KEY", base_url="https://api.example.com")

rules = client.rules.get()
print(rules)
```

## Features
- Works with the entire ProperProt API.
- Fully typed responses with Pydantic.
- Sychronous API calls using requests.
- Easily maintainable.

## Requirements
- Python >= 3.9
- requests >= 2.30.0
- pydantic >= 2.3.0