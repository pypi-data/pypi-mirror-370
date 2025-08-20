"""This module provides a helper for the OpenAPI specification."""

from __future__ import annotations

import logging
import re

from axmp_openapi_helper.openapi.axmp_api_models import SUPPORTED_METHODS, AxmpOpenAPI
from axmp_openapi_helper.openapi.fastapi.openapi_models import Operation
from axmp_openapi_helper.openapi.multi_openapi_spec import (
    APIServerConfig,
    AuthConfig,
    AuthenticationType,
    MethodSpec,
    MultiOpenAPISpecConfig,
)
from axmp_openapi_helper.openapi.operation import AxmpAPIOperation
from axmp_openapi_helper.utils.converter import Converter
from axmp_openapi_helper.wrapper.api_wrapper import AxmpAPIWrapper

logger = logging.getLogger(__name__)


class MultiOpenAPIHelper:
    """MultiOpenAPIHelper for ZMP ApiWrapper."""

    def __init__(self, multi_openapi_spec_config: MultiOpenAPISpecConfig):
        """Initialize the OpenAPIHelper."""
        self.multi_openapi_spec_config = multi_openapi_spec_config
        self._validate_multi_openapi_spec_config()

        self._openapi_servers: dict[str, APIServerConfig] = (
            self._initialize_openapi_servers()
        )
        self._all_operations: list[AxmpAPIOperation] = self._initialize_all_operations()
        # NOTE: clients are initialized after initialization
        # self._clients: dict[str, AxmpAPIWrapper] = self._initialize_clients()
        self._clients: dict[str, AxmpAPIWrapper] = {}

    def _validate_multi_openapi_spec_config(self):
        """Validate the multi-server API specification configuration."""
        path_method_set = set()
        for backend in self.multi_openapi_spec_config.backends:
            # check the spec file path and zmp open api
            if not backend.spec_file_path:
                raise ValueError(
                    f"Spec file path is required for backend: {backend.server_name}"
                )

            # check auth config
            if backend.auth_config:
                if backend.auth_config.type not in [
                    AuthenticationType.BASIC,
                    AuthenticationType.BEARER,
                    AuthenticationType.API_KEY,
                    AuthenticationType.NONE,
                ]:
                    raise ValueError(f"Invalid auth type: {backend.auth_config.type}")

                # NOTE: username and password are not required during the initialization because the username and password are set on the mcp server
                # issue https://github.com/cloudz-mp/axmp-openapi-helper/issues/46
                # if backend.auth_config.type == AuthenticationType.BASIC and (
                #     not backend.auth_config.username
                # ):
                #     raise ValueError(
                #         f"Username and password are required for basic auth: {backend.server_name}"
                #     )
                if backend.auth_config.type == AuthenticationType.API_KEY and (
                    not backend.auth_config.api_key_name
                    # NOTE: api_key_value is not required during the initialization because the api_key_value is set on the mcp server
                    # or not backend.auth_config.api_key_value
                ):
                    raise ValueError(
                        f"API key name and value are required for api key auth: {backend.server_name}"
                    )

                # NOTE: bearer token is not required during the initialization because the bearer token is set on the mcp server
                # if (
                #     backend.auth_config.type == AuthenticationType.BEARER
                #     and not backend.auth_config.bearer_token
                # ):
                #     raise ValueError(
                #         f"Bearer token is required for bearer auth: {backend.server_name}"
                #     )

            # check tool config
            if not backend.tool_config:
                raise ValueError(
                    f"Tool config is required for backend: {backend.server_name}"
                )

            if not backend.tool_config.api_maps and not backend.tool_config.route_maps:
                raise ValueError(
                    f"API maps or route maps are required for backend: {backend.server_name}"
                )

            # check api maps
            if backend.tool_config.api_maps:
                for api_map in backend.tool_config.api_maps:
                    # check path
                    if not api_map.path or not api_map.path.startswith("/"):
                        raise ValueError(
                            f"API map path is required and must start with /: {api_map.path}"
                        )
                    if api_map.path.endswith("/"):
                        raise ValueError(
                            f"API map path must not end with /: {api_map.path}"
                        )
                    if backend.base_path and not api_map.path.startswith(
                        backend.base_path
                    ):
                        raise ValueError(
                            f"API map path must start with base path: {api_map.path} and base path is {backend.base_path}"
                        )

                    # check methods
                    for method in api_map.methods:
                        method_name = None
                        if isinstance(method, str):
                            method_name = method.lower()
                            if method_name not in SUPPORTED_METHODS:
                                raise ValueError(f"Invalid method name: {method_name}")
                        elif isinstance(method, MethodSpec):
                            method_name = method.method.lower()
                            if method_name not in SUPPORTED_METHODS:
                                raise ValueError(f"Invalid method name: {method_name}")
                            if not method.tool_name and not method.description:
                                raise ValueError(
                                    f"Tool name and description are required for method: {method_name}"
                                )
                        else:
                            raise ValueError(f"Invalid method type: {type(method)}")

                        path_method = (
                            f"[{backend.server_name}:{api_map.path}:{method_name}]"
                        )
                        if path_method in path_method_set:
                            raise ValueError(
                                f"Duplicate operation found: {path_method}"
                            )
                        path_method_set.add(path_method)

            # check route maps
            if backend.tool_config.route_maps:
                for route_map in backend.tool_config.route_maps:
                    if (
                        not route_map.pattern
                        and not route_map.methods
                        and not route_map.tags
                    ):
                        raise ValueError(
                            f"At least one of pattern, methods, and tags is required for route map: {route_map}"
                        )
                    # check pattern whether it is valid regex
                    if route_map.pattern and route_map.pattern != "":
                        try:
                            re.compile(route_map.pattern)
                        except re.error:
                            raise ValueError(
                                f"Invalid regex pattern: {route_map.pattern}"
                            )

                    # check methods whether it is valid and in supported methods
                    if route_map.methods and len(route_map.methods) > 0:
                        for method in route_map.methods:
                            if method.lower() not in SUPPORTED_METHODS:
                                raise ValueError(f"Invalid method name: {method}")

                    # TODO: check tags whether it is valid and in supported tags

    def _initialize_openapi_servers(self) -> dict[str, APIServerConfig]:
        """Initialize the openapi servers."""
        return {
            backend.server_name: backend
            for backend in self.multi_openapi_spec_config.backends
        }

    def _initialize_all_operations(self) -> list[AxmpAPIOperation]:
        """Initialize the all operations."""
        operations: list[AxmpAPIOperation] = []

        for backend in self.multi_openapi_spec_config.backends:
            axmp_open_api: AxmpOpenAPI = None

            if backend.spec_file_path:
                axmp_open_api = AxmpOpenAPI.from_spec_file(backend.spec_file_path)
            else:
                raise ValueError(
                    f"Spec file path is required for backend: {backend.server_name}"
                )

            # generate operations from api maps
            if backend.tool_config.api_maps:
                operations.extend(
                    self._get_api_operation_from_api_maps(
                        backend=backend, axmp_open_api=axmp_open_api
                    )
                )

            # generate operations from route maps
            if backend.tool_config.route_maps:
                _route_map_operations = self._get_api_operation_from_route_maps(
                    backend=backend, axmp_open_api=axmp_open_api
                )
                # check the duplicate operations by path and method of the _route_map_operations in the operations
                for _operation in _route_map_operations:
                    if _operation.name not in [op.name for op in operations]:
                        operations.append(_operation)

        return operations

    def _get_api_operation_from_route_maps(
        self, *, backend: APIServerConfig, axmp_open_api: AxmpOpenAPI
    ) -> list[AxmpAPIOperation]:
        """Get API operations from route maps."""
        common_operations: list[tuple[str, str, Operation]] = []

        for route_map in backend.tool_config.route_maps:
            pattern_matched_operations: list[tuple[str, str, Operation]] = []
            tag_matched_operations: list[tuple[str, str, Operation]] = []
            method_matched_operations: list[tuple[str, str, Operation]] = []

            if route_map.pattern:
                pattern_matched_operations = (
                    axmp_open_api.get_operations_by_path_pattern(
                        regex=route_map.pattern
                    )
                )

            if route_map.tags and len(route_map.tags) > 0:
                for tag in route_map.tags:
                    tag_matched_operations.extend(
                        axmp_open_api.get_operations_by_tag(tag=tag)
                    )

            if route_map.methods and len(route_map.methods) > 0:
                for method in route_map.methods:
                    method_matched_operations.extend(
                        axmp_open_api.get_operations_by_method(method=method)
                    )

            # extract the common operations from pattern_matched_operations, tag_matched_operations, method_matched_operations
            # should exclude the empty *_matched_operations during the extract the common operations
            if pattern_matched_operations:
                if tag_matched_operations:
                    if method_matched_operations:
                        for path, method, operation in pattern_matched_operations:
                            if (path, method) in [
                                (path, method)
                                for path, method, _ in tag_matched_operations
                            ] and (path, method) in [
                                (path, method)
                                for path, method, _ in method_matched_operations
                            ]:
                                # check the duplicate operations by path and method of the common_operations
                                if (path, method, operation) not in common_operations:
                                    common_operations.append((path, method, operation))
                    else:
                        for path, method, operation in pattern_matched_operations:
                            if (path, method) in [
                                (path, method)
                                for path, method, _ in tag_matched_operations
                            ]:
                                # check the duplicate operations by path and method of the common_operations
                                if (path, method, operation) not in common_operations:
                                    common_operations.append((path, method, operation))
                else:
                    if method_matched_operations:
                        for path, method, operation in pattern_matched_operations:
                            if (path, method) in [
                                (path, method)
                                for path, method, _ in method_matched_operations
                            ]:
                                # check the duplicate operations by path and method of the common_operations
                                if (path, method, operation) not in common_operations:
                                    common_operations.append((path, method, operation))
                    else:
                        for path, method, operation in pattern_matched_operations:
                            # check the duplicate operations by path and method of the common_operations
                            if (path, method, operation) not in common_operations:
                                common_operations.append((path, method, operation))
            else:
                if tag_matched_operations:
                    if method_matched_operations:
                        for path, method, operation in tag_matched_operations:
                            if (path, method) in [
                                (path, method)
                                for path, method, _ in method_matched_operations
                            ]:
                                # check the duplicate operations by path and method of the common_operations
                                if (path, method, operation) not in common_operations:
                                    common_operations.append((path, method, operation))
                    else:
                        for path, method, operation in tag_matched_operations:
                            # check the duplicate operations by path and method of the common_operations
                            if (path, method, operation) not in common_operations:
                                common_operations.append((path, method, operation))
                else:
                    if method_matched_operations:
                        for path, method, operation in method_matched_operations:
                            # check the duplicate operations by path and method of the common_operations
                            if (path, method, operation) not in common_operations:
                                common_operations.append((path, method, operation))
                    else:
                        # NOTE: if all the *_matched_operations are empty, we should raise an error
                        raise ValueError(
                            f"All the *_matched_operations are empty for route map: {route_map}"
                        )

        return self._convert_operations_to_api_operations(
            backend=backend,
            axmp_open_api=axmp_open_api,
            operations=common_operations,
        )

    def _convert_operations_to_api_operations(
        self,
        *,
        backend: APIServerConfig,
        axmp_open_api: AxmpOpenAPI,
        operations: list[tuple[str, str, Operation]],
    ) -> list[AxmpAPIOperation]:
        """Convert operations to API operations."""
        api_operations: list[AxmpAPIOperation] = []
        for path, method, operation in operations:
            tool_name = Converter.generate_name_from_path(
                path=path,
                method=method,
                base_path=backend.base_path,
            )

            description = None
            if operation.description:
                description = operation.description
            else:
                description = ""

            query_params, path_params, request_body = (
                axmp_open_api.generate_models_by_path_and_method(
                    path=path, method=method
                )
            )

            api_operations.append(
                AxmpAPIOperation(
                    server_name=backend.server_name,
                    name=tool_name,
                    description=description,
                    path=path,
                    method=method,
                    query_params=query_params,
                    path_params=path_params,
                    request_body=request_body,
                )
            )

        return api_operations

    def _get_api_operation_from_api_maps(
        self, *, backend: APIServerConfig, axmp_open_api: AxmpOpenAPI
    ) -> list[AxmpAPIOperation]:
        """Get API operations from API maps."""
        operations: list[AxmpAPIOperation] = []

        for api_map in backend.tool_config.api_maps:  # type: ignore
            for method in api_map.methods:
                method_name = None
                tool_name = None
                description = None

                if isinstance(method, str):
                    method_name = method
                elif isinstance(method, MethodSpec):
                    method_name = method.method
                    description = method.description
                    tool_name = method.tool_name
                else:
                    raise ValueError(f"Invalid method type: {type(method)}")

                operation: Operation = axmp_open_api.get_operation_by_path_method(
                    path=api_map.path,
                    method=method_name,
                )
                query_params, path_params, request_body = (
                    axmp_open_api.generate_models_by_path_and_method(
                        path=api_map.path, method=method_name
                    )
                )

                # if tool_name is not provided, generate it from the path and method
                if not tool_name:
                    tool_name = Converter.generate_name_from_path(
                        path=api_map.path,
                        method=method_name,
                        base_path=backend.base_path,
                    )

                # duplicate check the tool_name in the operations
                # because the tool_name should be unique in the operations for the mcp server
                for op in operations:
                    if op.name == tool_name:
                        # NOTE: if the tool_name is duplicate, we should add a number to the tool_name
                        # to make it unique
                        tool_name = self._generate_unique_tool_name(
                            tool_name=tool_name, operations=operations
                        )
                        break

                # if description is not provided, generate it from the operation
                if not description:
                    if operation.description:
                        description = operation.description
                    else:
                        description = ""

                operations.append(
                    AxmpAPIOperation(
                        server_name=backend.server_name,
                        name=tool_name,
                        description=description,
                        path=api_map.path,
                        method=method_name,
                        query_params=query_params,
                        path_params=path_params,
                        request_body=request_body,
                    )
                )

        return operations

    def _generate_unique_tool_name(
        self, *, tool_name: str, operations: list[AxmpAPIOperation]
    ) -> str:
        """Generate the unique tool name."""
        if tool_name in [op.name for op in operations]:
            tool_name_index = tool_name.split("_")[-1]
            if tool_name_index.isdigit():
                tool_name = f"{tool_name.split('_')[:-1]}_{int(tool_name_index) + 1}"
            else:
                tool_name = f"{tool_name}_1"
        return tool_name

    def initialize_clients(self) -> None:
        """Initialize the clients."""
        clients: dict[str, AxmpAPIWrapper] = {}
        for server_name, openapi_server in self._openapi_servers.items():
            if openapi_server.auth_config:
                auth_config = openapi_server.auth_config
                if auth_config.type == AuthenticationType.BASIC:
                    if not auth_config.username:
                        raise ValueError(
                            f"Username is required for basic auth: {server_name}"
                        )
                    if not auth_config.password:
                        raise ValueError(
                            f"Password is required for basic auth: {server_name}"
                        )
                elif auth_config.type == AuthenticationType.API_KEY:
                    if not auth_config.api_key_name:
                        raise ValueError(
                            f"API key name is required for api key auth: {server_name}"
                        )
                    if not auth_config.api_key_value:
                        raise ValueError(
                            f"API key value is required for api key auth: {server_name}"
                        )
                elif auth_config.type == AuthenticationType.BEARER:
                    if not auth_config.bearer_token:
                        raise ValueError(
                            f"Bearer token is required for bearer auth: {server_name}"
                        )

            clients[server_name] = AxmpAPIWrapper(
                openapi_server.endpoint,
                auth_type=openapi_server.auth_config.type,
                username=openapi_server.auth_config.username,
                password=openapi_server.auth_config.password,
                bearer_token=openapi_server.auth_config.bearer_token,
                api_key_name=openapi_server.auth_config.api_key_name,
                api_key_value=openapi_server.auth_config.api_key_value,
                tls_verify=openapi_server.tls_verify,
                timeout=openapi_server.timeout,
            )

        self._clients = clients

    def update_openapi_server_auth_config(
        self, *, server_name: str, auth_config: AuthConfig
    ) -> None:
        """Update the auth config."""
        self._openapi_servers[server_name].auth_config = auth_config

    @property
    def openapi_servers(self) -> dict[str, APIServerConfig]:
        """Get the openapi servers."""
        return self._openapi_servers

    @property
    def all_operations(self) -> list[AxmpAPIOperation]:
        """Generate the operations from the multi-server API specification configuration."""
        if not self._all_operations:
            self._initialize_all_operations()

        return self._all_operations

    @property
    def clients(self) -> dict[str, AxmpAPIWrapper]:
        """Get the clients."""
        return self._clients

    def get_operations_by_server_name(
        self, *, server_name: str
    ) -> list[AxmpAPIOperation]:
        """Get the operations by server name."""
        return [op for op in self.all_operations if op.server_name == server_name]

    # NOTE: @deprecated, use Converter.generate_name_from_path instead
    def _generate_name_from_path(
        self, *, path: str, method: str, base_path: str | None = None
    ) -> str:
        """Generate the operation name from the path."""
        if base_path:
            if path.startswith(base_path):
                path = path.replace(base_path, "")
            else:
                # NOTE: if the path does not start with the base_path, it means the path is not in the base_path
                # e.g. /healthz is not in the base_path /api/alert/v1
                # raise ValueError(f"Path {path} does not start with prefix {base_path}")
                pass

        replaced_path = re.sub(r"[{}]", "", path)  # remove path params brackets
        replaced_path = re.sub(r"[/:~$-]", "_", replaced_path)  # replace /,:,$,~ with _

        return f"{method.lower()}{replaced_path}"

    async def run(self, *, name: str, args: dict | None = None) -> str:
        """Run the operation by name and args."""
        logger.debug(f"name: {name}")
        logger.debug(f"args: {args}")

        operation = next((op for op in self.all_operations if op.name == name), None)
        if not operation:
            raise ValueError(f"Operation {name} not found")

        if args is None:
            args = {}

        path_params = operation.path_params(**args) if operation.path_params else None
        query_params = (
            operation.query_params(**args) if operation.query_params else None
        )
        request_body = (
            operation.request_body(**args) if operation.request_body else None
        )

        logger.debug(f"path_params: {path_params}")
        logger.debug(f"query_params: {query_params}")
        logger.debug(f"request_body: {request_body}")

        client = self._clients[operation.server_name]

        logger.debug(f"client: {client}")

        return await client.run(
            operation.method,
            operation.path,
            path_params=path_params,
            query_params=query_params,
            request_body=request_body,
        )

    def get_all_tags(self) -> list[str]:
        """Get all tags of the operations."""
        tags = []

        for backend in self.multi_openapi_spec_config.backends:
            axmp_open_api: AxmpOpenAPI = AxmpOpenAPI.from_spec_file(
                backend.spec_file_path
            )

            tags.extend(axmp_open_api.get_tags())

        return list(set(tags))

    def get_tags(self, *, server_name: str) -> list[str]:
        """Get all tags of the operations by server name."""
        open_api_server = self._openapi_servers[server_name]
        axmp_open_api: AxmpOpenAPI = AxmpOpenAPI.from_spec_file(
            open_api_server.spec_file_path
        )

        return axmp_open_api.get_tags()

    # get all operations by tag
    def get_all_operations_by_tag(
        self, *, tag: str
    ) -> list[tuple[str, str, Operation]]:
        """Get operations by tag."""
        operations: list[tuple[str, str, Operation]] = []
        for backend in self.multi_openapi_spec_config.backends:
            axmp_open_api: AxmpOpenAPI = AxmpOpenAPI.from_spec_file(
                backend.spec_file_path
            )

            operations.extend(axmp_open_api.get_operations_by_tag(tag=tag))

        return operations

    def get_operations_by_tag(
        self, *, server_name: str, tag: str
    ) -> list[tuple[str, str, Operation]]:
        """Get operations by tag."""
        open_api_server = self._openapi_servers[server_name]
        axmp_open_api: AxmpOpenAPI = AxmpOpenAPI.from_spec_file(
            open_api_server.spec_file_path
        )

        return axmp_open_api.get_operations_by_tag(tag=tag)

    def get_all_operations_by_path_pattern(
        self, *, regex: str
    ) -> list[tuple[str, str, Operation]]:
        """Get operations by path pattern."""
        operations: list[tuple[str, str, Operation]] = []
        for backend in self.multi_openapi_spec_config.backends:
            axmp_open_api: AxmpOpenAPI = AxmpOpenAPI.from_spec_file(
                backend.spec_file_path
            )

            operations.extend(axmp_open_api.get_operations_by_path_pattern(regex=regex))

        return operations

    def get_operations_by_path_pattern(
        self, *, server_name: str, regex: str
    ) -> list[tuple[str, str, Operation]]:
        """Get operations by path pattern."""
        open_api_server = self._openapi_servers[server_name]
        axmp_open_api: AxmpOpenAPI = AxmpOpenAPI.from_spec_file(
            open_api_server.spec_file_path
        )

        return axmp_open_api.get_operations_by_path_pattern(regex=regex)

    def get_all_operations_by_method(
        self, *, method: str
    ) -> list[tuple[str, str, Operation]]:
        """Get operations by method."""
        operations: list[tuple[str, str, Operation]] = []
        for backend in self.multi_openapi_spec_config.backends:
            axmp_open_api: AxmpOpenAPI = AxmpOpenAPI.from_spec_file(
                backend.spec_file_path
            )

            operations.extend(axmp_open_api.get_operations_by_method(method=method))

        return operations

    def get_operations_by_method(
        self, *, server_name: str, method: str
    ) -> list[tuple[str, str, Operation]]:
        """Get operations by method."""
        open_api_server = self._openapi_servers[server_name]
        axmp_open_api: AxmpOpenAPI = AxmpOpenAPI.from_spec_file(
            open_api_server.spec_file_path
        )

        return axmp_open_api.get_operations_by_method(method=method)

    async def close(self) -> None:
        """Close the clients."""
        for client in self._clients.values():
            await client.close()
