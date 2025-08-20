# Copyright (c) Beijing Volcano Engine Technology Ltd.

import logging
from datetime import datetime, timezone

import requests

from .error import SCRIPT_EXEC_COMMON_ERROR_CODE, SUCCESS
from .response import Response
from .sign import send_openapi_request

logger = logging.getLogger(__name__)


class OpenAPIClient:
    """Volc OpenAPI Client."""

    def __init__(
        self,
        top_service_name: str,
        ak: str,
        sk: str,
        region: str,
    ):
        self.top_service_name = top_service_name
        self.ak = ak
        self.sk = sk
        self.region = region

    def call_api(self, version, method, query, header, action, body):
        """Execute openapi."""
        exit_code = SUCCESS

        now = datetime.now(timezone.utc)
        session_token = None
        try:
            response = send_openapi_request(
                self.top_service_name,
                version,
                self.region,
                method,
                now,
                query,
                header,
                self.ak,
                self.sk,
                session_token,
                action,
                body,
            )
            if response.status_code == 200:
                message = response.json()
            else:
                exit_code = response.status_code
                message = response.text

        except requests.RequestException as e:
            exit_code = SCRIPT_EXEC_COMMON_ERROR_CODE
            message = str(e)

        return Response(exit_code, message)
