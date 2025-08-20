# Copyright (c) Beijing Volcano Engine Technology Ltd.

import hashlib
import hmac
import logging
from urllib.parse import quote

import requests

Host = "open.volcengineapi.com"
ContentType = "application/json"

logger = logging.getLogger(__name__)


def norm_query(params):
    """norm_query."""
    query = ""
    for key in sorted(params.keys()):
        if isinstance(params[key], list):
            for k in params[key]:
                query = (
                    query
                    + quote(key, safe="-_.~", encoding="utf-8")
                    + "="
                    + quote(k, safe="-_.~", encoding="utf-8")
                    + "&"
                )
        else:
            query = (
                query
                + quote(key, safe="-_.~", encoding="utf-8")
                + "="
                + quote(params[key], safe="-_.~", encoding="utf-8")
                + "&"
            )
    query = query[:-1]
    return query.replace("+", "%20")


def hmac_sha256(key: bytes, content: str):
    """hmac_sha256."""
    return hmac.new(key, content.encode("utf-8"), hashlib.sha256).digest()


def hash_sha256(content: str):
    """hash_sha256."""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def send_openapi_request(
    service,
    version,
    region,
    method,
    date,
    query,
    header,
    ak,
    sk,
    session_token,
    action,
    body,
):
    """Prepare the credentials. The fields 'service' and 'region' are fixed, and
    'ak'/'sk' represents 'AccessKeyID'/'SecretAccessKey' respectively.
    """
    credential = {
        "access_key_id": ak,
        "secret_access_key": sk,
        "service": service,
        "region": region,
    }
    # Initialize the request.
    request_param = {
        "body": body,
        "host": Host,
        "path": "/",
        "method": method,
        "content_type": ContentType,
        "date": date,
        "query": {"Action": action, "Version": version, **query},
    }
    if body is None:
        request_param["body"] = ""

    # Next: prepare the header.
    x_date = request_param["date"].strftime("%Y%m%dT%H%M%SZ")
    short_x_date = x_date[:8]
    x_content_sha256 = hash_sha256(request_param["body"])
    sign_result = {
        "Host": request_param["host"],
        "X-Content-Sha256": x_content_sha256,
        "X-Date": x_date,
        "Content-Type": request_param["content_type"],
    }

    # Next: prepare the request string to be signed.
    signed_headers_str = "content-type;host;x-content-sha256;x-date"
    canonical_request_str = "\n".join(
        [
            request_param["method"].upper(),
            request_param["path"],
            norm_query(request_param["query"]),
            "\n".join(
                [
                    "content-type:" + request_param["content_type"],
                    "host:" + request_param["host"],
                    "x-content-sha256:" + x_content_sha256,
                    "x-date:" + x_date,
                ]
            ),
            "",
            signed_headers_str,
            x_content_sha256,
        ]
    )
    hashed_canonical_request = hash_sha256(canonical_request_str)

    logger.info("Canonical Request String:\n%s", canonical_request_str)
    logger.info("Hashed Canonical Request:\n%s", hashed_canonical_request)

    credential_scope = "/".join(
        [short_x_date, credential["region"], credential["service"], "request"]
    )
    string_to_sign = (
        f"HMAC-SHA256\n{x_date}\n{credential_scope}\n{hashed_canonical_request}"
    )
    logger.info("String to Sign:\n%s", string_to_sign)

    # Next: create the signature of the request.
    k_date = hmac_sha256(credential["secret_access_key"].encode("utf-8"), short_x_date)
    k_region = hmac_sha256(k_date, credential["region"])
    k_service = hmac_sha256(k_region, credential["service"])
    k_signing = hmac_sha256(k_service, "request")
    signature = hmac_sha256(k_signing, string_to_sign).hex()
    logger.info("Signature:\n%s", signature)

    # Next: set the signature in header and send request.
    sign_result["Authorization"] = (
        "HMAC-SHA256 Credential={}, SignedHeaders={}, Signature={}".format(
            credential["access_key_id"] + "/" + credential_scope,
            signed_headers_str,
            signature,
        )
    )
    header = {**header, **sign_result}
    if session_token:
        header = {**header, "X-Security-Token": session_token}
    return requests.request(
        method=method,
        url="https://{}{}".format(request_param["host"], request_param["path"]),
        headers=header,
        params=request_param["query"],
        data=request_param["body"].encode("utf-8"),
        timeout=30,
    )
