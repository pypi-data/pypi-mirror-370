# Binoauth Python SDK

A multi-tenant authentication and authorization Python SDK that supports OAuth2, OpenID Connect, API keys, and multiple authentication methods.

## Features

- **Admin API**: Management endpoints for tenants, clients, users, API keys, and provider settings
- **Tenant API**: Authentication endpoints for login, signup, OAuth2 flows, magic links, phone OTP, and user profile management
- **Multiple Authentication Methods**: API keys, Bearer tokens, session cookies
- **Auto-generated from OpenAPI**: Always up-to-date with the latest API specifications
- **Type-safe**: Full type hints and Pydantic models
- **Python 3.9+**: Modern Python support

## Installation

```bash
pip install binoauth
```

For development:
```bash
pip install -e .[dev]
```

## Quick Start

### Admin API Usage

```python
from binoauth import BinoauthAdmin

# Initialize admin client
admin = BinoauthAdmin(
    host="https://api.auth.example.com",
    access_token="your_admin_token"
)

# List tenants
tenants = admin.api.list_tenants_api_v1_tenants_get()

# Create a new client
client_data = {
    "name": "My App",
    "redirect_uris": ["https://myapp.com/callback"]
}
new_client = admin.api.create_client_api_v1_clients_post(client_data)
```

### Tenant API Usage

```python
from binoauth import BinoauthTenant

# Initialize tenant client
tenant = BinoauthTenant(
    host="https://tenant.auth.example.com",
    api_key="your_api_key"
)

# User signup
signup_data = {
    "email": "user@example.com",
    "password": "secure_password"
}
response = tenant.auth.signup_api_v1_auth_signup_post(signup_data)

# OAuth2 authorization
auth_url = tenant.oauth2.authorize_api_v1_oauth2_authorize_get(
    client_id="your_client_id",
    redirect_uri="https://yourapp.com/callback",
    response_type="code"
)
```

### Context Manager Usage

```python
# Both classes support context managers
with BinoauthAdmin(host="...", access_token="...") as admin:
    tenants = admin.api.list_tenants_api_v1_tenants_get()

with BinoauthTenant(host="...", api_key="...") as tenant:
    response = tenant.auth.login_api_v1_auth_login_post(login_data)
```

## Development Setup

### Prerequisites

- Python 3.9+
- Git
- OpenAPI Generator CLI (for code generation)

### Development Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd binoauth-python-sdk
```

2. Install development dependencies:
```bash
pip install -e .[dev]
```

3. Install pre-commit hooks:
```bash
pre-commit install
```

### Development Commands

#### Code Generation
```bash
# Regenerate SDK from latest OpenAPI specs
./codegen.sh
```

#### Testing
```bash
# Run all tests
python -m pytest

# Run tests with coverage
python -m pytest --cov=binoauth

# Run specific test file
python -m pytest binoauth/admin/test/test_admin_api.py
```

#### Code Quality & Linting
```bash
# Format code
black binoauth/

# Sort imports
isort binoauth/

# Lint code
flake8 binoauth/

# Type checking (manual only, auto-generated code conflicts)
mypy binoauth/__init__.py --ignore-missing-imports --allow-untyped-calls

# Run all quality checks
pre-commit run --all-files
```

#### Version Management
```bash
# Bump patch version (1.0.0 → 1.0.1)
bump-my-version bump patch

# Bump minor version (1.0.0 → 1.1.0)
bump-my-version bump minor

# Bump major version (1.0.0 → 2.0.0)
bump-my-version bump major

# Show what would be changed (dry run)
bump-my-version bump --dry-run --verbose patch
```

#### Package Publishing
```bash
# Install publishing tools
pip install build twine

# Build the package
python -m build

# Upload to Test PyPI (recommended first)
twine upload --repository testpypi dist/*

# Upload to production PyPI
twine upload dist/*

# Check package on PyPI
pip install binoauth  # test installation

# Automated release (recommended)
./release.sh patch  # or minor/major
```

#### Release Process

The project includes an automated release script that handles the complete publishing workflow:

```bash
# Make sure you're on main branch with clean working directory
git checkout main
git pull origin main

# Run automated release (handles testing, building, and publishing)
./release.sh patch   # for bug fixes (1.0.0 → 1.0.1)
./release.sh minor   # for new features (1.0.0 → 1.1.0)
./release.sh major   # for breaking changes (1.0.0 → 2.0.0)
```

The release script:
1. Verifies you're on main branch with clean working directory
2. Runs all tests and quality checks
3. Shows version bump preview and asks for confirmation
4. Bumps version and creates git commit/tag
5. Builds the package (source + wheel)
6. Uploads to Test PyPI first for verification
7. Asks for final confirmation before production upload
8. Uploads to production PyPI
9. Pushes git tag to remote repository

**Prerequisites for publishing:**
- PyPI account with API tokens
- Configure `~/.pypirc` with your tokens (see `.pypirc.template`)

```

## Architecture

### Package Structure

```shell
binoauth/
├── __init__.py                 # Main SDK with convenience wrappers
├── admin/                      # Admin API (auto-generated)
│   ├── api/                    # API endpoint classes
│   ├── models/                 # Pydantic data models
│   ├── docs/                   # Auto-generated documentation
│   └── test/                   # Unit tests
└── tenant/                     # Tenant API (auto-generated)
    ├── api/                    # API endpoint classes
    ├── models/                 # Pydantic data models
    ├── docs/                   # Auto-generated documentation
    └── test/                   # Unit tests
```

### High-Level Design

The SDK provides two main convenience wrapper classes:

- **`BinoauthAdmin`**: Wraps the admin API for tenant/client/user management
- **`BinoauthTenant`**: Wraps the tenant API for authentication operations

Both classes handle:
- Configuration management
- Multiple authentication methods
- Context manager support
- Error handling

### Code Generation

The `binoauth/admin/` and `binoauth/tenant/` directories contain auto-generated code from OpenAPI specifications. **Never manually edit files in these directories.**

The `./codegen.sh` script:
1. Downloads latest OpenAPI specs from production endpoints
2. Generates Python clients using OpenAPI Generator
3. Maintains unified package structure
4. Preserves manually maintained convenience wrappers

## Authentication Methods

### 1. API Keys (Recommended for Backend Services)
```python
tenant = BinoauthTenant(
    host="https://tenant.auth.example.com",
    api_key="your_api_key"
)
```

### 2. Bearer Tokens (OAuth2/JWT)
```python
admin = BinoauthAdmin(
    host="https://api.auth.example.com",
    access_token="your_jwt_token"
)
```

### 3. Session Cookies
Session authentication is handled automatically by the underlying HTTP client when cookies are present.

## Contributing

1. **Code Style**: This project uses Black (88 character line length) and isort for formatting
2. **Type Hints**: All new code should include proper type annotations
3. **Testing**: Write tests for new functionality in the appropriate test directories
4. **Linting**: All code must pass flake8, mypy, and other quality checks
5. **Pre-commit**: Install and use pre-commit hooks for automated quality checks

### Important Notes

- **Auto-generated Code**: Never edit files in `binoauth/admin/` or `binoauth/tenant/` directories
- **Version Management**: Use `bump-my-version` for version updates
- **Dependencies**: Keep core dependencies minimal; add development tools to `[dev]` extra
- **Multi-tenant Architecture**: Admin API operates on public tenant, Tenant API is tenant-specific

## License
MIT

## Support
coming soon!
