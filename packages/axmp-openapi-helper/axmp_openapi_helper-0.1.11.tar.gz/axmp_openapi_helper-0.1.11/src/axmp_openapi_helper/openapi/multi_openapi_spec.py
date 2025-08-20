"""This module provides a model for the mixed API specification."""

from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import List

from pydantic import BaseModel


class AuthenticationType(str, Enum):
    """Authentication type model."""

    NONE = "None"
    BASIC = "Basic"
    BEARER = "Bearer"
    API_KEY = "ApiKey"


class MethodSpec(BaseModel):
    """A model for the method specification."""

    method: str
    tool_name: str | None = None
    description: str | None = None


class APIMap(BaseModel):
    """A model for the API simple specification."""

    path: str
    methods: List[str | MethodSpec]


class RouteMap(BaseModel):
    """A model for the route map."""

    methods: List[str] | None = None
    tags: List[str] | None = None
    pattern: str | None = None


class ToolConfig(BaseModel):
    """A model for the tool configuration."""

    api_maps: List[APIMap] | None = None
    route_maps: List[RouteMap] | None = None


class AuthConfig(BaseModel):
    """A model for the authentication configuration."""

    type: AuthenticationType = AuthenticationType.NONE
    username: str | None = None
    password: str | None = None
    api_key_name: str | None = None
    api_key_value: str | None = None
    bearer_token: str | None = None


class APIServerConfig(BaseModel):
    """A model for the API server configuration."""

    server_name: str
    endpoint: str
    base_path: str | None = None
    timeout: float = 10
    tls_verify: bool = True
    spec_file_path: str | Path
    # NOTE: open_api_spec is not needed any more
    # open_api_spec: AxmpOpenAPI | None = None
    tool_config: ToolConfig
    auth_config: AuthConfig


class MultiOpenAPISpecConfig(BaseModel):
    """MultiOpenAPISpecConfig is a model that contains the configuration for the multi-server API specification.

    ```json
    {
        "backends": [
            {
                "server_name": "zcp-alert-backend",
                "endpoint": "https://zcp-alert-backend.com",
                "base_path": "/api/alert/v1",
                "tls_verify": false,
                "timeout": 10,
                "auth_config": {
                    "type": "basic",
                    "username": "admin",
                    "password": "password"
                },
                "spec_file_path": "openapi_spec/zcp_spec/alert_openapi_spec.json",
                "tool_config": {
                    "api_maps": [
                        {
                            "path":"/api/alert/v1/alerts",
                            "methods": ["get", "post"]
                        },
                        {
                            "path":"/api/alert/v1/alerts/webhook",
                            "methods": ["post"]
                        },
                        {
                            "path":"/api/alert/v1/alert/priorities",
                            "methods": ["get"]
                        }
                    ]
                }
            },
            {
                "server_name": "example-backend",
                "endpoint": "https://example-backend.com",
                "base_path": "/api/example/v1",
                "spec_file_path": "openapi_spec/example_spec/test_spec.json",
                "tls_verify": true,
                "timeout": 10,
                "auth_config": {
                    "type": "api_key",
                    "custom_header_api_key_name": "X-API-KEY",
                    "custom_header_api_key_value": "1234567890"
                },
                "tool_config": {
                    "api_maps": [
                        {
                            "path":"/api/example/v1/test",
                            "methods": [
                                {
                                    "method": "post",
                                    "tool_name": "create_test",
                                    "description": "Create test"
                                }
                            ]
                        }
                    ],
                    "route_maps": [
                        {
                            "pattern": r".*",
                            "methods": ["get"],
                            "tags": ["*"]
                        }
                    ]
                }
            },
            {
                "server_name": "zcp-alert-backend",
                "endpoint": "https://zcp-alert-backend.com",
                "base_path": "/api/alert/v1",
                "spec_file_path": "openapi_spec/zcp_spec/alert_openapi_spec.json",
                "tls_verify": true,
                "timeout": 10,
                "auth_config": {
                    "type": "bearer",
                    "bearer_token": "1234567890"
                },
                "tool_config": {
                    "route_maps": [
                        {
                            "pattern": "^/api/alert/v1/channels/.*",
                            "methods": ["get"],
                            "tags": []
                        },
                        {
                            "pattern": "^/api/alert/v1/admin/.*",
                            "methods": ["post"],
                            "tags": ["alerts"]
                        }
                    ]
                }
            }
        ]
    }
    ```
    """

    backends: List[APIServerConfig]

    @classmethod
    def from_multi_server_spec_file(
        cls, file_path: str | Path
    ) -> MultiOpenAPISpecConfig:
        """Load the multi-server API specification from a file."""
        with open(file_path) as f:
            return cls.model_validate_json(f.read())
