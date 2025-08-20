# Copyright (c) Beijing Volcano Engine Technology Ltd.

SUCCESS = 0
# Common error, like that caused by environment
SCRIPT_EXEC_COMMON_ERROR_CODE = 1
# Inner error
SCRIPT_EXEC_INNER_ERROR_CODE = 1
# Unknown error, like un caught error
SCRIPT_EXEC_UNHANDLED_ERROR_CODE = 101

"""The definitions of errors in las-infra."""


# Configuration related =========================


class ConfigurationError(Exception):
    """Configuration error."""

    def __init__(self, message):
        super().__init__(message)


# OpenAPI related ====================================


class CertificationError(Exception):
    """Exception raised when get credentials."""

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class OpenAPIError(Exception):
    """Exception raised when request OpenAPI."""

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)
