"""This module provides a runner for the AxmpAPIModels."""

import asyncio
import json
import logging
import logging.config

from axmp_openapi_helper.openapi.axmp_api_models import AxmpOpenAPI
from axmp_openapi_helper.utils.converter import Converter

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
    """Run the axmp api models."""
    # axmp_open_api = AxmpOpenAPI.from_spec_file(
    #     file_path="runner/openapi/zcp/zcp_alert_backend_openapi_spec.json"
    # )

    # openapi is a dict case
    # openapi: dict = json.loads(
    #     open("runner/openapi/zcp/zcp_mcm_backend_openapi_spec.json").read()
    # )
    # axmp_open_api = AxmpOpenAPI.from_spec_dict(data=openapi)

    # testing
    # operations = axmp_open_api.get_operations_by_tag_method_pattern(
    #     tags=["alert", "channel"], methods=["delete"], regex=r"^/api/alert/v1/.*"
    # )
    # test case that causes errors in version 0.1.7
    # operations = axmp_open_api.get_operations_by_tag_method_pattern(
    #     tags=["alert", "channel"], methods=["get","post","put","delete"], regex=r"^/api/v1/csp/{csp}/auth/check"
    # )
    # test case: uppercase methods are supported 
    # operations = axmp_open_api.get_operations_by_tag_method_pattern(
    #     tags=["alert", "channel"], methods=["GET"], regex=r"^/aaaaaa"
    # )

    #test case: ignore content tpye application/xml, application/x-www-form-urlencoded
    openapi: dict = json.loads(
        open("runner/openapi/pet_store_3.0.json").read()
    )
    axmp_open_api = AxmpOpenAPI.from_spec_dict(data=openapi)
    operations = axmp_open_api.get_operations_by_tag_method_pattern(
        tags=["alert", "channel"], methods=["get","post","put","delete"], regex=r"^/aaaaaa"
    )
    tools = Converter.operations_to_tools(
        server_name="zcp_alert_backend",
        base_path="/api/alert/v1",
        axmp_open_api=axmp_open_api,
        operations=operations,
    )

    # print the tools
    for tool in tools:
        print("-" * 100)
        # print(f"server_name: {tool.server_name}")
        print(f"tool_name: {tool.name}")
        # print(f"tool_description: {tool.description}")
        print(f"tool_path: {tool.path}")
        print(f"tool_method: {tool.method}")
        # print(f"tool_query_params: {tool.query_params}")
        # print(f"tool_path_params: {tool.path_params}")
        print(f"tool_request_body: {tool.request_body}")
    print("tool count: ", len(tools))


if __name__ == "__main__":
    asyncio.run(main())
