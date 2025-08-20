# Kivera SDK

Python library to interact with the Kivera Graphql API

### Installation

```
pip install kivera-sdk
```

### Example Usage
```
import kivera
import json

creds = "/path/to/user-api-key.json"
with open(creds) as f:
  creds_json = json.load(f)
client = kivera.Client(credentials=creds_json)
print(client.ListOrganizationPolicyFunctions())
print(client.ListRulesV4())
```
