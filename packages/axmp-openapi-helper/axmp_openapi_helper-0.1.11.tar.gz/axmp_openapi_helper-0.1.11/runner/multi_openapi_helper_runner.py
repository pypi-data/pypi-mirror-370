"""This module provides a runner for the ZMP OpenAPI Helper."""

import asyncio
import logging
import logging.config

from axmp_openapi_helper import (
    MultiOpenAPISpecConfig,
)
from axmp_openapi_helper.multi_openapi_helper import MultiOpenAPIHelper
from axmp_openapi_helper.openapi.multi_openapi_spec import (
    AuthConfig,
    AuthenticationType,
)
from axmp_openapi_helper.openapi.operation import AxmpAPIOperation

logging.config.fileConfig("logging.conf", disable_existing_loggers=False)
logging.getLogger("axmp_openapi_helper.openapi.multi_openapi_helper").setLevel(
    logging.INFO
)
logging.getLogger("axmp_openapi_helper.openapi.axmp_api_models").setLevel(logging.INFO)
logging.getLogger("axmp_openapi_helper.openapi.operation").setLevel(logging.INFO)
logging.getLogger("axmp_openapi_helper.openapi.fastapi.fastapi_models").setLevel(
    logging.DEBUG
)
logger = logging.getLogger("appLogger")
logger.setLevel(logging.DEBUG)


async def main():
    """Run the multi openapi helper."""
    multi_openapi_spec_config = MultiOpenAPISpecConfig.from_multi_server_spec_file(
        file_path="runner/openapi/zmp_multi_openapi_spec.json"
    )

    multi_openapi_helper = MultiOpenAPIHelper(
        multi_openapi_spec_config=multi_openapi_spec_config
    )

    api_servers = multi_openapi_helper.openapi_servers
    for server_name, server in api_servers.items():
        print("-" * 100)
        print(server_name)
        print(server.endpoint)
        print(server.base_path)
        print(server.spec_file_path)

    for server_name, server in api_servers.items():
        multi_openapi_helper.update_openapi_server_auth_config(
            server_name=server_name,
            auth_config=AuthConfig(
                type=AuthenticationType.API_KEY,
                api_key_name="X-Access-Key",
                api_key_value="zmp-09bae73d-9f59-491a-ae06-7747e8f79883",
            ),
        )
    multi_openapi_helper.initialize_clients()

    operations: list[AxmpAPIOperation] = multi_openapi_helper.all_operations
    for i, operation in enumerate(operations):
        print("-" * 100)
        print(
            f"{i}:{operation.server_name}:{operation.method}:{operation.name}:{operation.path}"
        )
        # print(operation.description)
        # print(operation.args_schema)
        # print(operation.path_params)
        # print(operation.query_params)
        # print(operation.request_body)

    # response = await multi_openapi_helper.run(
    #     name="get_alerts", args={"priorities": ["P1", "P2"]}
    # )
    # print(response)

    # response = await multi_openapi_helper.run(name="get_clusters", args=None)
    # print(response)

    # tags = multi_openapi_helper.get_all_tags()
    # print("-" * 100)
    # print("all tags")
    # print(tags)

    # tags = multi_openapi_helper.get_tags(server_name="zcp-alert-backend")
    # print("-" * 100)
    # print("tags by server name")
    # print(tags)

    # path_method_operations: list[tuple[str, str, Operation]] = (
    #     multi_openapi_helper.get_all_operations_by_path_pattern(regex="^/api/alert/v1.*")
    # )
    # print("-" * 100)
    # print("operations by path pattern")
    # for path, method, operation in path_method_operations:
    #     print(f"{method}:{path}")

    # path_method_operations: list[tuple[str, str, Operation]] = (
    #     multi_openapi_helper.get_all_operations_by_method(method="put")
    # )
    # print("-" * 100)
    # print("operations by method")
    # for path, method, operation in path_method_operations:
    #     print(f"{method}:{path}")

    # path_method_operations: list[tuple[str, str, Operation]] = (
    #     multi_openapi_helper.get_all_operations_by_tag(tag="alert")
    # )
    # print("-" * 100)
    # print("operations by tag")
    # for path, method, operation in path_method_operations:
    #     print(f"{method}:{path}")

    await multi_openapi_helper.close()


if __name__ == "__main__":
    asyncio.run(main())
