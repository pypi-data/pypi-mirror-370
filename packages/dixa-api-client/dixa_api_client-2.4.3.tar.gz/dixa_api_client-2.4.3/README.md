# Dixa API Wrapper

[![Python](https://img.shields.io/pypi/pyversions/dixa-api-client.svg)](https://badge.fury.io/py/dixa-api-client)
[![PyPI](https://badge.fury.io/py/dixa-api-client.svg)](https://badge.fury.io/py/dixa-api-client)
[![PyPI](https://github.com/ChemicalLuck/dixa-api-client/actions/workflows/python-publish.yml/badge.svg)](https://github.com/ChemicalLuck/dixa-api-client/actions/workflows/python-publish.yml)
![PyPI - Downloads](https://img.shields.io/pypi/dm/dixa-api-client)

## Installation

```bash
pip install dixa-api-client
```

## Usage

```python
from dixa import Dixa

client = Dixa(api_key='XXXXX')

agents = client.v1.Agents.list()

for agent in agents:
    print(agent['id'])
```

For more details on the content of the reponses, visit the [official dixa API docs](https://docs.dixa.io/openapi/dixa-api/v1/overview/).

## Resources Available
### v1
- Agents
- Analytics
- Contact Endpoints
- Conversations
- Custom Attributes
- End Users
- Queues
- Tags
- Teams
- Webhooks

## Resources

- [dixa API v1](https://docs.dixa.io/openapi/dixa-api/v1/overview/)

## License

[MIT](LICENSE)
