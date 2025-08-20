# Copyright (c) Beijing Volcano Engine Technology Ltd.


class Response:
    """Volcengine OpenAPI response."""

    def __init__(self, status_code, message):
        self._status_code = status_code
        self._message = message

    @property
    def status_code(self):
        """status_code."""
        return self._status_code

    @status_code.setter
    def status_code(self, value):
        self._status_code = value

    @property
    def message(self):
        """Message."""
        return self._message

    @message.setter
    def message(self, value):
        self._message = value

    def to_dict(self):
        """to_dict."""
        return {"status_code": self._status_code, "message": self._message}
