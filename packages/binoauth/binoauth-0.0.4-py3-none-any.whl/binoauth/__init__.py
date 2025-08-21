"""
Binoauth Python SDK.

A multi-tenant authentication and authorization API client library that supports
OAuth2, OpenID Connect, API keys, and multiple authentication methods.

The SDK provides two main modules:
- Admin API (binoauth.admin): Management endpoints for tenants, clients, users, API keys
- Tenant API (binoauth.tenant): Authentication endpoints for login, signup, OAuth2 flows
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional, Union

if TYPE_CHECKING:
    from types import TracebackType

__version__ = "0.0.4"


# Import main API classes for convenient access
try:
    from binoauth.admin import AdminApi, AdminAuthenticationApi
    from binoauth.admin import HealthApi as AdminHealthApi
    from binoauth.admin.api_client import ApiClient as AdminApiClient
    from binoauth.admin.configuration import Configuration as AdminConfiguration
    from binoauth.admin.exceptions import ApiException as AdminApiException
except ImportError:
    # Admin module not generated yet
    AdminApi = None  # type: ignore[misc]
    AdminAuthenticationApi = None  # type: ignore[misc]
    AdminHealthApi = None  # type: ignore[misc]
    AdminConfiguration = None  # type: ignore[misc]
    AdminApiClient = None  # type: ignore[misc]
    AdminApiException = None  # type: ignore[misc]

try:
    from binoauth.tenant import (
        AuthenticationApi,
        ExternalAuthApi,
        OAuth2Api,
        OpenidApi,
        SystemApi,
        UserProfileApi,
    )
    from binoauth.tenant.api_client import ApiClient as TenantApiClient
    from binoauth.tenant.configuration import Configuration as TenantConfiguration
    from binoauth.tenant.exceptions import ApiException as TenantApiException
except ImportError:
    # Tenant module not generated yet
    AuthenticationApi = None  # type: ignore[misc]
    OAuth2Api = None  # type: ignore[misc]
    ExternalAuthApi = None  # type: ignore[misc]
    UserProfileApi = None  # type: ignore[misc]
    SystemApi = None  # type: ignore[misc]
    OpenidApi = None  # type: ignore[misc]
    TenantConfiguration = None  # type: ignore[misc]
    TenantApiClient = None  # type: ignore[misc]
    TenantApiException = None  # type: ignore[misc]


class BinoauthAdmin:
    """
    Convenience wrapper for Binoauth Admin API.

    Provides management endpoints for tenants, clients, users, and API keys.
    Requires Bearer token authentication.

    Usage:
        admin = BinoauthAdmin(host="https://api.auth.example.com", access_token="your_token")
        tenants = admin.api.list_tenants_api_v1_tenants_get()
    """

    def __init__(self, host: str, access_token: Optional[str] = None) -> None:
        """
        Initialize the Binoauth Admin API client.

        Args:
            host: The host URL for the admin API
            access_token: Bearer token for authentication
        """
        if AdminConfiguration is None:
            raise ImportError(
                "Admin API not available. Run './codegen.sh' to generate the SDK."
            )

        self.configuration = AdminConfiguration(host=host)
        if access_token:
            self.configuration.access_token = access_token

        self.client = AdminApiClient(self.configuration)
        self.api = AdminApi(self.client)
        self.auth = AdminAuthenticationApi(self.client)
        self.health = AdminHealthApi(self.client)

    def __enter__(self) -> BinoauthAdmin:
        """Enter the context manager."""
        return self

    def __exit__(
        self,
        _exc_type: Optional[type[BaseException]],
        _exc_val: Optional[BaseException],
        _exc_tb: Optional[TracebackType],
    ) -> None:
        """Exit the context manager and clean up resources."""
        pass


class BinoauthTenant:
    """
    Convenience wrapper for Binoauth Tenant API.

    Provides authentication endpoints for login, signup, OAuth2 flows, and user management.
    Supports multiple authentication methods: API keys, Bearer tokens, and session cookies.

    Usage:
        tenant = BinoauthTenant(host="https://tenant.auth.example.com")
        response = tenant.auth.login_api_v1_auth_login_post(login_request)
    """

    def __init__(
        self,
        host: str,
        api_key: Optional[str] = None,
        access_token: Optional[str] = None,
    ) -> None:
        """
        Initialize the Binoauth Tenant API client.

        Args:
            host: The host URL for the tenant API
            api_key: API key for authentication
            access_token: Bearer token for authentication
        """
        if TenantConfiguration is None:
            raise ImportError(
                "Tenant API not available. Run './codegen.sh' to generate the SDK."
            )

        self.configuration = TenantConfiguration(host=host)
        if api_key:
            self.configuration.api_key["X-API-Key"] = api_key
        if access_token:
            self.configuration.access_token = access_token

        self.client = TenantApiClient(self.configuration)
        self.auth = AuthenticationApi(self.client)
        self.oauth2 = OAuth2Api(self.client)
        self.external_auth = ExternalAuthApi(self.client)
        self.profile = UserProfileApi(self.client)
        self.system = SystemApi(self.client)
        self.openid = OpenidApi(self.client)

    def __enter__(self) -> BinoauthTenant:
        """Enter the context manager."""
        return self

    def __exit__(
        self,
        _exc_type: Optional[type[BaseException]],
        _exc_val: Optional[BaseException],
        _exc_tb: Optional[TracebackType],
    ) -> None:
        """Exit the context manager and clean up resources."""
        pass


# Export main classes for easy imports
__all__ = [
    "__version__",
    "BinoauthAdmin",
    "BinoauthTenant",
    # Admin API classes
    "AdminApi",
    "AdminAuthenticationApi",
    "AdminHealthApi",
    "AdminConfiguration",
    "AdminApiClient",
    "AdminApiException",
    # Tenant API classes
    "AuthenticationApi",
    "OAuth2Api",
    "ExternalAuthApi",
    "UserProfileApi",
    "SystemApi",
    "OpenidApi",
    "TenantConfiguration",
    "TenantApiClient",
    "TenantApiException",
]
