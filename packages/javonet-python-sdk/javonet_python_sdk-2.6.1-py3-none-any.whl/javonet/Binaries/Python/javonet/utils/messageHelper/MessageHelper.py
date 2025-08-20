# File: javonet/utils/messageHelper/MessageHelper.py
import datetime
import importlib.metadata
import os
import platform
import socket
import threading
import urllib.request
import urllib.error
import json

from javonet.utils.UtilsConst import UtilsConst


def __get_host_name():
    try:
        return socket.gethostname()
    except socket.error:
        return "Unknown Host"


def __get_package_version():
    try:
        return importlib.metadata.version("javonet-python-sdk")
    except importlib.metadata.PackageNotFoundError:
        return None


address = "https://dc.services.visualstudio.com/v2/track"
instrumentation_key = os.environ.get("JAVONET_INSTRUMENTATION_KEY", "2c751560-90c8-40e9-b5dd-534566514723")
calling_runtime_name = "Python"
javonet_version = __get_package_version()
node_name = __get_host_name()
os_name = platform.system()


class MessageHelper:

    @staticmethod
    def send_message_to_app_insights(operation_name, message):
        thread = threading.Thread(target=MessageHelper.send_message_to_app_insights_sync,
                                  args=(operation_name, message))
        thread.start()

    @staticmethod
    def send_message_to_app_insights_sync(operation_name, message):
        try:
            formatted_datetime = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
            license_key = UtilsConst.get_license_key()

            json_payload = {
                "name": "AppEvents",
                "time": formatted_datetime,
                "iKey": instrumentation_key,
                "tags": {
                    "ai.application.ver": javonet_version,
                    "ai.cloud.roleInstance": node_name,
                    "ai.operation.id": "0",
                    "ai.operation.parentId": "0",
                    "ai.operation.name": operation_name,
                    "ai.internal.sdkVersion": "javonet:2",
                    "ai.internal.nodeName": node_name
                },
                "data": {
                    "baseType": "EventData",
                    "baseData": {
                        "ver": 2,
                        "name": message,
                        "properties": {
                            "OperatingSystem": os_name,
                            "LicenseKey": license_key,
                            "CallingTechnology": calling_runtime_name
                        }
                    }
                }
            }

            data = json.dumps(json_payload).encode("utf-8")
            req = urllib.request.Request(address, data=data, headers={'Content-Type': 'application/json'})
            with urllib.request.urlopen(req) as response:
                status_code = response.getcode()
            return status_code
        except urllib.error.HTTPError as e:
            return e.code
        except Exception:
            pass