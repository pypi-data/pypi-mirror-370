# MontyCloud SDK

A Python SDK for interacting with the MontyCloud DAY2 API.

## Features

- AWS-style client factories for simplified access
- Secure authentication with API key and API secret key
- Multi-tenant context management
- Comprehensive error handling with retry logic
- Strongly typed models using Pydantic
- CLI interface for common operations

## Requirements

- Python 3.11 or higher

## Installation

```bash
pip install day2
```

## Quick Start

### Using the SDK

#### Method 1: AWS-style Client Factories

```python
import day2

# Use module-level client factories (automatically creates a default session)
tenants = day2.tenant().list_tenants()

for tenant in tenants.tenants:
    print(f"Tenant: {tenant.name} (ID: {tenant.id})")

# List assessments
assessments = day2.assessment().list_assessments(
    tenant_id="tenant-123",
    status="PENDING"
)

for assessment in assessments.assessments:
    print(f"Assessment: {assessment.name} (ID: {assessment.id})")
```

#### Method 2: Explicit Session

```python
import day2

# Create a session with API key
session = day2.Session(api_key="your-api-key", api_secret_key="your-api-secret-key")

# List tenants
tenants = session.tenant.list_tenants()

for tenant in tenants.tenants:
    print(f"Tenant: {tenant.name} (ID: {tenant.id})")

# Set tenant context
session.set_tenant("tenant-123")

# List assessments in the tenant
assessments = session.assessment.list_assessments(tenant_id="tenant-123", status="PENDING")

for assessment in assessments.assessments:
    print(f"Assessment: {assessment.name} (ID: {assessment.id})")
```

### Using the CLI

Configure authentication:

```bash
day2 auth configure --api-key your-api-key --api-secret-key your-api-secret-key
```

List tenants:

```bash
day2 tenant list
```

Get details of a specific tenant:

```bash
day2 tenant get tenant-123
```

List questions for a specific pillar in an assessment:

```bash
day2 assessment questions tenant-123 assessment-456 operational-excellence
```

Create a new assessment:

```bash
day2 assessment create tenant-123 \
    --name "My Assessment" \
    --description "My assessment description" \
    --review-owner "user@example.com" \
    --scope '{"AccountId": "123456789012"}' \
    --lenses "AWS Well-Architected Framework"
```

## Authentication

The SDK supports authentication with both an API key and an API secret key. You can provide these credentials in several ways:

1. Directly in code:
   ```python
   # Simplified API
   session = day2.Session(api_key="your-api-key", api_secret_key="your-secret-key")

   # With API secret key
   session = day2.Session(
       api_key="your-api-key",
       api_secret_key="your-api-secret-key"
   )
   ```

2. Environment variables:
   ```bash
   export DAY2_API_KEY="your-api-key"
   export DAY2_API_SECRET_KEY="your-api-secret-key"
   ```
   ```python
   # Will use the environment variables
   session = day2.Session()
   # Or use the default session
   session = day2.get_default_session()
   ```

3. Configuration file:
   ```bash
   # Using the CLI to configure
   day2 auth configure --api-key your-api-key --api-secret-key your-api-secret-key
   ```
   ```python
   # Will use the configuration file
   session = day2.Session()
   # Or use the default session
   session = day2.get_default_session()
   ```

## Multi-Tenant Support

The SDK supports multi-tenant operations through session-based tenant context:

```python
# Create a session
session = day2.Session(api_key="your-api-key", api_secret_key="your-secret-key")

# Set tenant context
session.set_tenant("org-123")

# Operations will now be performed in the context of the tenant
assessments = session.assessment.list_assessments(tenant_id="tenant-123", status="PENDING")

# Switch to a different tenant
session.set_tenant("tenant-456")

# Operations will now be performed in the context of the new tenant
assessments = session.assessment.list_assessments(tenant_id="tenant-456", status="PENDING")

# Clear tenant context
session.clear_tenant()
```

You can also use the default session with module-level client factories:

```python
# Get the default session and set tenant context
default_session = day2.get_default_session()
default_session.set_tenant("org-123")

# Now all module-level client factories will use this tenant context
assessments = day2.assessment().list_assessments(tenant_id="tenant-123", status="PENDING")
```

## Error Handling

The SDK provides comprehensive error handling with custom exceptions:

```python
import day2
from day2.exceptions import (
    ClientError,
    ServerError,
    ValidationError,
    ResourceNotFoundError,
    AuthenticationError,
    TenantContextError,
)

try:
    # Using module-level client factory
    tenant = day2.tenant().get_tenant("tenant-nonexistent")
except ResourceNotFoundError as e:
    print(f"Resource not found: {e}")
except ClientError as e:
    print(f"Client error: {e}")
except ServerError as e:
    print(f"Server error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
