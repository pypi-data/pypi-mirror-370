# Connector SDK Types

This package contains the generated types for the Lumos Connector SDK. These types are automatically generated from the TypeSpec definitions and provide type-safe interfaces for all connector operations.

## Installation

```console
pip install connector-sdk-types
```

## Usage

This package is typically used as a dependency of the main `connector-py` package. The types are available for import:

```python
from connector_sdk_types import ListAccountsRequest, ListAccountsResponse
```

## Generated Types

This package contains all the generated Pydantic models that define the request and response structures for connector capabilities, including:

- Account models (ListAccountsRequest, CreateAccountRequest, etc.)
- Entitlement models (AssignEntitlementRequest, etc.)
- Authentication models (BasicCredential, OAuthCredential, etc.)
- Error models (Error, ErrorCode, etc.)
- And many more...

## Note

**This package contains auto-generated code.** Do not modify the generated models directly. Changes should be made to the TypeSpec definitions in the main repository, which will regenerate these types.

## License

`connector-sdk-types` is distributed under the terms of the [Apache 2.0](./LICENSE.txt) license.
