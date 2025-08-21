# Neurograph Core Python SDK

The Neurograph Core Python SDK provides convenient, type-safe access to the Neurograph Core API.  
This guide covers local installation, authentication, and your first API call.

---

## 🚀 Quickstart

1. Activate your Python 3.12 virtual environment

2. Install the SDK

```bash
pip install neurograph-core
```

3. Use your service token to make a call
```python
from neurograph.v1.configuration import Configuration
from neurograph.v1.api_client import ApiClient
from neurograph.v1.api import atlas_api

config = Configuration()
config.host = "https://core-staging.neurograph.io"
config.api_key['ApiKeyAuth'] = "<your service token>"
config.api_key_prefix['ApiKeyAuth'] = "Bearer"

with ApiClient(config) as client:
    atlas = atlas_api.AtlasApi(client)
    print(atlas.api_v1_atlas_versions_get())
    
```
---