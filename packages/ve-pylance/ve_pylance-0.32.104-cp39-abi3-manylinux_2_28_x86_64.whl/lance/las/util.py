import json
import os
import subprocess

from .las_api import LasApi

"""
获取path的vepfs ID，只支持绝对路径的解析

"""
def get_filesystem(path) -> str:
    if not os.path.exists(path):
        print(f"Error: Path does not exist: {path}")
        return ""

    command = f"df {path}"
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        output_lines = result.stdout.strip().split("\n")
        if len(output_lines) > 1:
            filesystem = output_lines[1].split()[0]
            return filesystem
        else:
            print(f"Could not determine filesystem for {path}")
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")
        print("Error output:")
        print(e.stderr)
    return ""


def callback(evt):
    # 过滤mode为create的事件
    if evt.target == "lance::dataset_events" and evt.args.get("event") == "loading":
        # 解析trace event
        event_data = {
            "SdkType": "Lance",
            "LastAccessTime": evt.args.get("timestamp"),
            "DatasetPath": evt.args.get("uri"),
            "FilesystemId": get_filesystem(evt.args.get("uri")),
            "SdkVersion": evt.args.get("client_version"),
        }

        # 发送到火山控制台
        try:
            print("send to volc console, evt:", event_data)
            response = LasApi().lance_callback(body=json.dumps(event_data))
            print("send to volc console, response:", response)
        except Exception as e:
            print("send to volc console failed:", e)
