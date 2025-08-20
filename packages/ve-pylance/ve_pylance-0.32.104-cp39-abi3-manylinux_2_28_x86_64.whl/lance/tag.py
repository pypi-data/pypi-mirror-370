# ByteDance Volcengine EMR, Copyright 2024.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""The module contains all the business logic for tagging tos buckets ."""

import fcntl
import functools
import json
import logging
import os
import re
import threading
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Optional, Tuple

from volcengine.ApiInfo import ApiInfo
from volcengine.base.Service import Service
from volcengine.Credentials import Credentials
from volcengine.ServiceInfo import ServiceInfo

ENV_NAME_TOS_BUCKET_TAG_ENABLE = "TOS_BUCKET_TAG_ENABLE"
ENV_NAME_VOLC_REGION = "VOLC_REGION"

PUT_TAG_ACTION_NAME = "PutBucketDoubleMeterTagging"
GET_TAG_ACTION_NAME = "GetBucketTagging"
EMR_OPEN_API_VERSION = "2022-12-29"
OPEN_API_HOST = os.environ.get("OPEN_API_HOST", "open.volcengineapi.com")
ACCEPT_HEADER_KEY = "accept"
ACCEPT_HEADER_JSON_VALUE = "application/json"

THREAD_POOL_SIZE = 2
TAGGED_BUCKETS_FILE = "/tmp/.emr_tagged_buckets"

CONNECTION_TIMEOUT_DEFAULT_SECONDS = 60 * 5
SOCKET_TIMEOUT_DEFAULT_SECONDS = 60 * 5

service_info_map = {
    "cn-beijing": ServiceInfo(
        OPEN_API_HOST,
        {
            ACCEPT_HEADER_KEY: ACCEPT_HEADER_JSON_VALUE,
        },
        Credentials("", "", "emr", "cn-beijing"),
        CONNECTION_TIMEOUT_DEFAULT_SECONDS,
        SOCKET_TIMEOUT_DEFAULT_SECONDS,
        "http",
    ),
    "cn-guangzhou": ServiceInfo(
        OPEN_API_HOST,
        {
            ACCEPT_HEADER_KEY: ACCEPT_HEADER_JSON_VALUE,
        },
        Credentials("", "", "emr", "cn-guangzhou"),
        CONNECTION_TIMEOUT_DEFAULT_SECONDS,
        SOCKET_TIMEOUT_DEFAULT_SECONDS,
        "http",
    ),
    "cn-shanghai": ServiceInfo(
        OPEN_API_HOST,
        {
            ACCEPT_HEADER_KEY: ACCEPT_HEADER_JSON_VALUE,
        },
        Credentials("", "", "emr", "cn-shanghai"),
        CONNECTION_TIMEOUT_DEFAULT_SECONDS,
        SOCKET_TIMEOUT_DEFAULT_SECONDS,
        "http",
    ),
    "ap-southeast-1": ServiceInfo(
        OPEN_API_HOST,
        {
            ACCEPT_HEADER_KEY: ACCEPT_HEADER_JSON_VALUE,
        },
        Credentials("", "", "emr", "ap-southeast-1"),
        CONNECTION_TIMEOUT_DEFAULT_SECONDS,
        SOCKET_TIMEOUT_DEFAULT_SECONDS,
        "http",
    ),
    "cn-beijing-qa": ServiceInfo(
        OPEN_API_HOST,
        {
            ACCEPT_HEADER_KEY: ACCEPT_HEADER_JSON_VALUE,
        },
        Credentials("", "", "emr_qa", "cn-beijing"),
        CONNECTION_TIMEOUT_DEFAULT_SECONDS,
        SOCKET_TIMEOUT_DEFAULT_SECONDS,
        "http",
    ),
    "cn-beijing-selfdrive": ServiceInfo(
        OPEN_API_HOST,
        {
            ACCEPT_HEADER_KEY: ACCEPT_HEADER_JSON_VALUE,
        },
        Credentials("", "", "emr", "cn-beijing-selfdrive"),
        CONNECTION_TIMEOUT_DEFAULT_SECONDS,
        SOCKET_TIMEOUT_DEFAULT_SECONDS,
        "http",
    ),
    "cn-shanghai-autodriving": ServiceInfo(
        "emr.cn-shanghai-autodriving.volcengineapi.com",
        {
            ACCEPT_HEADER_KEY: ACCEPT_HEADER_JSON_VALUE,
        },
        Credentials("", "", "emr", "cn-shanghai-autodriving"),
        CONNECTION_TIMEOUT_DEFAULT_SECONDS,
        SOCKET_TIMEOUT_DEFAULT_SECONDS,
        "https",
    ),
    "cn-beijing-autodriving": ServiceInfo(
        "emr.cn-beijing-autodriving.volcengineapi.com",
        {
            ACCEPT_HEADER_KEY: ACCEPT_HEADER_JSON_VALUE,
        },
        Credentials("", "", "emr", "cn-beijing-autodriving"),
        CONNECTION_TIMEOUT_DEFAULT_SECONDS,
        SOCKET_TIMEOUT_DEFAULT_SECONDS,
        "https",
    ),
}

api_info = {
    PUT_TAG_ACTION_NAME: ApiInfo(
        "POST",
        "/",
        {"Action": PUT_TAG_ACTION_NAME, "Version": EMR_OPEN_API_VERSION},
        {},
        {},
    ),
    GET_TAG_ACTION_NAME: ApiInfo(
        "GET",
        "/",
        {"Action": GET_TAG_ACTION_NAME, "Version": EMR_OPEN_API_VERSION},
        {},
        {},
    ),
}


def find_bucket_key(tos_path: str) -> Tuple[str, str]:
    """It's a helper function to find bucket and key pair.

    It receives a tos path such that the path
    is of the form: bucket/key.
    It will return the bucket and the key represented by the tos path.
    """
    bucket_format_list = [
        # asw protocol pattern
        re.compile(r"^s3://(?P<bucket>[^/]+)/(?P<key>.*)$"),
        re.compile(
            r"^(?P<bucket>arn:(aws).*:s3:[a-z\-0-9]*:[0-9]{12}:accesspoint[:/][^/]+)/?"
            r"(?P<key>.*)$"
        ),
        re.compile(
            r"^(?P<bucket>arn:(aws).*:s3-outposts:[a-z\-0-9]+:[0-9]{12}:outpost[/:]"
            r"[a-zA-Z0-9\-]{1,63}[/:](bucket|accesspoint)[/:][a-zA-Z0-9\-]{1,63})[/:]?(?P<key>.*)$"
        ),
        re.compile(
            r"^(?P<bucket>arn:(aws).*:s3-outposts:[a-z\-0-9]+:[0-9]{12}:outpost[/:]"
            r"[a-zA-Z0-9\-]{1,63}[/:]bucket[/:]"
            r"[a-zA-Z0-9\-]{1,63})[/:]?(?P<key>.*)$"
        ),
        re.compile(
            r"^(?P<bucket>arn:(aws).*:s3-object-lambda:[a-z\-0-9]+:[0-9]{12}:"
            r"accesspoint[/:][a-zA-Z0-9\-]{1,63})[/:]?(?P<key>.*)$"
        ),
        # tos protocol pattern
        re.compile(r"^tos://(?P<bucket>[^/]+)/(?P<key>.*)$"),
        re.compile(
            r"^(?P<bucket>:tos:[a-z\-0-9]*:[0-9]{12}:accesspoint[:/][^/]+)/?"
            r"(?P<key>.*)$"
        ),
        re.compile(
            r"^(?P<bucket>:tos-outposts:[a-z\-0-9]+:[0-9]{12}:outpost[/:]"
            # pylint: disable=line-too-long
            r"[a-zA-Z0-9\-]{1,63}[/:](bucket|accesspoint)[/:][a-zA-Z0-9\-]{1,63})[/:]?(?P<key>.*)$"
        ),
        re.compile(
            r"^(?P<bucket>:tos-outposts:[a-z\-0-9]+:[0-9]{12}:outpost[/:]"
            r"[a-zA-Z0-9\-]{1,63}[/:]bucket[/:]"
            r"[a-zA-Z0-9\-]{1,63})[/:]?(?P<key>.*)$"
        ),
        re.compile(
            r"^(?P<bucket>:tos-object-lambda:[a-z\-0-9]+:[0-9]{12}:"
            r"accesspoint[/:][a-zA-Z0-9\-]{1,63})[/:]?(?P<key>.*)$"
        ),
    ]
    for bucket_format in bucket_format_list:
        match = bucket_format.match(tos_path)
        if match:
            return match.group("bucket"), match.group("key")
    tos_components = tos_path.split("/", 1)
    bucket = tos_components[0]
    tos_key = ""
    if len(tos_components) > 1:
        tos_key = tos_components[1]
    return bucket, tos_key


def parse_region(endpoint):
    region = None
    parts = endpoint.split(".")

    if len(parts) == 3:
        # Endpoint is formatted like 'tos-<region>.volces.com'
        if "tos-s3-" in parts[0]:
            region = parts[0].replace("tos-s3-", "")
        elif "tos-" in parts[0]:
            region = parts[0].replace("tos-", "")
    elif len(parts) == 4:
        # Endpoint is formatted like
        # '<bucket>.tos-<region>.volces.com'
        if "tos-s3-" in parts[1]:
            region = parts[1].replace("tos-s3-", "")
        elif "tos-" in parts[1]:
            region = parts[1].replace("tos-", "")
    elif len(parts) == 6:
        # Endpoint is formatted like
        # '<ep-id>.tos.<region>.privatelink.volces.com'
        region = parts[2]
    elif len(parts) == 7:
        # Endpoint is formatted like
        # '<bucket>.<ep-id>.tos.<region>.privatelink.volces.com'
        region = parts[3]

    logging.debug("Parsed region [%s] from endpoint [%s]", region, endpoint)
    return region


def tag_bucket(uri, storage_options) -> None:
    """Tag bucket."""
    try:
        tag_enabled = os.environ.get(
            ENV_NAME_TOS_BUCKET_TAG_ENABLE, "true"
        ).lower() == "true" and str(uri).startswith(("s3", "s3a", "tos"))
        if not tag_enabled:
            logging.debug("The tos bucket tag is not enabled.")
            return

        logging.debug("The tos bucket tag is enabled.")

        bucket, _ = find_bucket_key(uri)
        logging.debug("The bucket is %s", bucket)

        if storage_options is None:
            logging.debug("The storage_options is none, will not init tag manager.")
            return

        ak = storage_options.get("access_key_id")
        sk = storage_options.get("secret_access_key")
        session_token = storage_options.get("session_token")
        endpoint = storage_options.get("aws_endpoint")

        region = parse_region(endpoint)

        can_tag = (ak and sk) or session_token
        if not can_tag:
            logging.debug("The ak, sk etc is none, will not init tag manager.")
            return

        bucket_tag_mgr = BucketTagMgr(
            ak,
            sk,
            session_token,
            region,
        )

        if not bucket or not region:
            logging.debug("The bucket or region is empty, will not tag bucket.")
            return

        bucket_tag_mgr.add_bucket_tag(bucket)
    except Exception as e:
        logging.warning("skip tagging bucket due to warning : %s", str(e))


class BucketTagAction(Service):
    """BucketTagAction is a class to manage the tag of bucket."""

    _instance_lock = threading.Lock()

    def __new__(cls, *args: Any, **kwargs: Any) -> Any:
        """Singleton."""
        if not hasattr(BucketTagAction, "_instance"):
            with BucketTagAction._instance_lock:
                if not hasattr(BucketTagAction, "_instance"):
                    BucketTagAction._instance = object.__new__(cls)
        return BucketTagAction._instance

    def __init__(
        self,
        key: Optional[str],
        secret: Optional[str],
        session_token: Optional[str],
        region: str,
    ) -> None:
        """Init BucketTagAction."""
        super().__init__(self.get_service_info(region), self.get_api_info())
        if key:
            self.set_ak(key)

        if secret:
            self.set_sk(secret)

        if session_token:
            self.set_session_token(session_token)

    @staticmethod
    def get_api_info() -> dict:
        """Get api info."""
        return api_info

    @staticmethod
    def get_service_info(region: str) -> ServiceInfo:
        """Get service info."""
        service_info = service_info_map.get(region)
        if service_info:
            logging.debug("The service name is : %s", service_info.credentials.service)
            return service_info

        raise Exception("Do not support region: %s", region)

    def put_bucket_tag(self, bucket: str) -> tuple[str, bool]:
        """Put tag for bucket."""
        params = {
            "Bucket": bucket,
        }

        try:
            res = self.json(PUT_TAG_ACTION_NAME, params, json.dumps(""))
            res_json = json.loads(res)
            logging.debug("Put tag for bucket %s successfully: %s .", bucket, res_json)
            return bucket, True
        except Exception as e:
            logging.debug("Put tag for bucket %s failed: %s .", bucket, e)
            return bucket, False

    def get_bucket_tag(self, bucket: str) -> bool:
        """Get tag for bucket."""
        params = {
            "Bucket": bucket,
        }
        try:
            res = self.get(GET_TAG_ACTION_NAME, params)
            res_json = json.loads(res)
            logging.debug("The get bucket tag's response is %s", res_json)
            return True
        except Exception as e:
            logging.debug("Get tag for %s is failed: %s", bucket, e)
            return False


def singleton(cls: Any) -> Any:
    """Singleton decorator."""
    _instances = {}

    @functools.wraps(cls)
    def get_instance(*args: Any, **kwargs: Any) -> Any:
        if cls not in _instances:
            _instances[cls] = cls(*args, **kwargs)
        return _instances[cls]

    return get_instance


@singleton
class BucketTagMgr:
    """BucketTagMgr is a class to manage the tag of bucket."""

    def __init__(
        self,
        key: Optional[str],
        secret: Optional[str],
        session_token: Optional[str],
        region: str,
    ):
        """Init BucketTagMgr."""
        self.executor = ThreadPoolExecutor(max_workers=THREAD_POOL_SIZE)
        self.cached_bucket_set: set = set()
        self.key = key
        self.secret = secret
        self.session_token = session_token
        self.region = region

        actual_region = os.environ.get(ENV_NAME_VOLC_REGION)
        if actual_region:
            logging.debug(
                "Get the region from %s env, value: %s.",
                ENV_NAME_VOLC_REGION,
                actual_region,
            )
        else:
            actual_region = self.region

        self.bucket_tag_service = BucketTagAction(
            self.key, self.secret, self.session_token, actual_region
        )

    def add_bucket_tag(self, bucket: str) -> None:
        """Add tag for bucket."""
        collect_bucket_set = {bucket}

        if not collect_bucket_set - self.cached_bucket_set:
            return

        if os.path.exists(TAGGED_BUCKETS_FILE):
            with open(TAGGED_BUCKETS_FILE, "r") as file:
                tagged_bucket_from_file_set = set(file.read().split(" "))

                logging.debug(
                    "Marked tagged buckets in the file : %s",
                    tagged_bucket_from_file_set,
                )
            self.cached_bucket_set |= tagged_bucket_from_file_set

        need_tag_buckets = collect_bucket_set - self.cached_bucket_set
        logging.debug("Need to tag buckets : %s", need_tag_buckets)

        for res in self.executor.map(
            self.bucket_tag_service.put_bucket_tag, need_tag_buckets
        ):
            if res[1]:
                self.cached_bucket_set.add(res[0])

        with open(TAGGED_BUCKETS_FILE, "w") as fw:
            fcntl.flock(fw, fcntl.LOCK_EX)
            fw.write(" ".join(self.cached_bucket_set))
            fcntl.flock(fw, fcntl.LOCK_UN)
            fw.close()
