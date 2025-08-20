"""Converter for OpenAPI operations to API operations."""

import re

from axmp_openapi_helper.openapi.axmp_api_models import AxmpOpenAPI
from axmp_openapi_helper.openapi.fastapi.openapi_models import Operation
from axmp_openapi_helper.openapi.operation import AxmpAPIOperation


class Converter:
    """Converter for OpenAPI operations to API operations."""

    @classmethod
    def operations_to_tools(
        cls,
        *,
        server_name: str,
        base_path: str,
        axmp_open_api: AxmpOpenAPI,
        operations: list[tuple[str, str, Operation]],
    ) -> list[AxmpAPIOperation]:
        """Convert operations to API operations."""
        tools: list[AxmpAPIOperation] = []
        for path, method, operation in operations:
            tool_name = cls.generate_name_from_path(
                path=path,
                method=method,
                base_path=base_path,
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

            tools.append(
                AxmpAPIOperation(
                    server_name=server_name,
                    name=tool_name,
                    description=description,
                    path=path,
                    method=method,
                    query_params=query_params,
                    path_params=path_params,
                    request_body=request_body,
                )
            )

        return tools

    @classmethod
    def generate_name_from_path(
        cls, *, path: str, method: str, base_path: str | None = None
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

        if method.lower() == "get":
            return f"get{replaced_path}"
        elif method.lower() == "post":
            return f"create{replaced_path}"
        elif method.lower() == "put":
            return f"update{replaced_path}"
        elif method.lower() == "delete":
            return f"delete{replaced_path}"
        elif method.lower() == "patch":
            return f"patch{replaced_path}"
        else:
            return f"{method.lower()}{replaced_path}"
