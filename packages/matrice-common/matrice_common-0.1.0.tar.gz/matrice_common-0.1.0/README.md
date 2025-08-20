
# matrice\_common

**matrice\_common** is a high-performance, Cython-compiled Python package providing reusable utilities for Matrice.ai services.
It offers ready-to-use authentication classes, error handling helpers, and general-purpose functions with complete type stubs for IDEs.

## Features

* **Cython Compiled** – Optimized performance via C extensions.
* **Authentication Utilities** – Refresh token and access key-based authentication.
* **Error Handling** – Rich error logging with Kafka producer support.
* **Utility Functions** – Helpers for caching, dependency management, and duplicate checks.
* **Type Hints & Stubs** – `.pyi` stubs for full IDE autocomplete and docstring support.
* **Modular Design** – Clear separation of auth, utils, and RPC components.

## Installation

```bash
pip install matrice_common --upgrade
```

## Example Usage

```python
from matrice_common.token_auth import RefreshToken, AuthToken
from matrice_common.utils import log_errors

# Example: Create auth instance
refresh = RefreshToken(access_key="YOUR_ACCESS_KEY", secret_key="YOUR_SECRET_KEY")
auth = AuthToken(access_key="YOUR_ACCESS_KEY", secret_key="YOUR_SECRET_KEY", refresh_token=refresh)

# Example: Use decorator for automatic error logging
@log_errors(default_return="failed")
def risky_function(x):
    return 10 / x

print(risky_function(0))
```
