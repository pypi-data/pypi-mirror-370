# Copyright (c) Beijing Volcano Engine Technology Ltd.

import json
import logging
import os
import time
import traceback

from .top_openapi.error import SCRIPT_EXEC_COMMON_ERROR_CODE, SUCCESS, OpenAPIError
from .top_openapi.open_api_client import OpenAPIClient
from .top_openapi.response import Response

logger = logging.getLogger(__name__)
LAS_TOP_DEFAULT_ACTION_VERSION = "2024-06-30"
LAS_LANCE_CALLBACK_ACTION = "HandleSdkCallback"
DEFAULT_REGION = "cn-beijing"
# NOTE: 这里的service name需要和火山侧的service name一致, 否则会报错，线上是las
DEFAULT_SERVICE_NAME = "las"


class LasApi:
    """Las Api."""

    def __init__(self, api_client=None):
        if api_client is None:
            if os.getenv("LANCE_SDK_AK") is None or os.getenv("LANCE_SDK_SK") is None:
                raise ValueError("LANCE_SDK_AK and LANCE_SDK_SK must be set")

            api_client = OpenAPIClient(
                top_service_name=os.getenv("LANCE_SDK_SERVICE") or DEFAULT_SERVICE_NAME,
                ak=os.getenv("LANCE_SDK_AK"),
                sk=os.getenv("LANCE_SDK_SK"),
                region=os.getenv("LANCE_SDK_REGION") or DEFAULT_REGION,
            )
        self.api_client = api_client

    def lance_callback(self, body):
        """Lance callback with simple retry mechanism."""
        max_retries = 3
        retry_delay = 1  # 1 second

        for attempt in range(max_retries):
            response = None
            try:
                response = self.api_client.call_api(
                    LAS_TOP_DEFAULT_ACTION_VERSION,
                    "POST",
                    {},
                    {},
                    LAS_LANCE_CALLBACK_ACTION,
                    body,
                )
                response_json = json.dumps(response.to_dict())
                logger.info("api call response: %s", response_json)
                if response.status_code != SUCCESS:
                    raise OpenAPIError(
                        "call lance callback open api failed, status_code: %s, "
                        "message: %s" % (response.status_code, response.message)
                    )
                return response.message
            except Exception as e:  # noqa: BLE001
                logger.info("call lance callback open api failed: %s", e)
                traceback.print_exc()
                if attempt == max_retries - 1:  # Last attempt
                    response = Response(
                        status_code=SCRIPT_EXEC_COMMON_ERROR_CODE, message=str(e)
                    )
                    response_json = json.dumps(response.to_dict())
                    logger.info("api call response: %s", response_json)
                    raise OpenAPIError(
                        "call lance callback open api failed, status_code: %s, "
                        "message: %s" % (response.status_code, response.message)
                    )
                else:
                    logger.info("Retrying in %s seconds...", retry_delay)
                    time.sleep(retry_delay)
        return response.message
