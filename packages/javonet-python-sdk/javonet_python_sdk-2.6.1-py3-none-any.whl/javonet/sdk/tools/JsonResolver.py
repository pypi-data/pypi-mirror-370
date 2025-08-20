import json
import os

from javonet.utils.UtilsConst import UtilsConst


class JsonResolver:
    def __init__(self, config_source: str):
        self.config_source = config_source
        self.json_object = None
        self.runtimes = None

        json_text = ""

        # Get text from config source
        try:
            if os.path.exists(config_source):
                with open(config_source, 'r') as f:
                    json_text = f.read()
            else:
                json_text = config_source
        except (OSError, IOError):
            raise ValueError(f"Configuration source is not a valid JSON. Check your configuration:\n{self.config_source}")
        except Exception:
            json_text = config_source
        # Parse json text
        try:
            self.json_object = json.loads(json_text)
        except Exception:
            raise ValueError(f"Configuration source is not a valid JSON. Check your configuration:\n{self.config_source}")

        UtilsConst.set_config_source(self.config_source)

    def get_license_key(self) -> str:
        try:
            return self.json_object["licenseKey"]
        except Exception:
            raise ValueError("License key not found in configuration source. Check your configuration source.")

    def get_working_directory(self) -> str:
        try:
            return self.json_object["workingDirectory"]
        except Exception:
            raise ValueError("Working directory not found in configuration source. Check your configuration source.")

    def _get_runtimes(self) -> None:
        self.runtimes = self.json_object["runtimes"]

    def _get_runtime(self, runtime_name: str, config_name: str) -> dict:
        self._get_runtimes()
        runtime = self.runtimes[runtime_name]

        if isinstance(runtime, list):
            for item in runtime:
                if item["name"] == config_name:
                    return item
        else:
            if runtime["name"] == config_name:
                return runtime

        raise ValueError(
            f"Runtime config {config_name} not found in configuration source for runtime {runtime_name}. Check your configuration source.")

    def _get_runtime_name(self, runtime_name: str, config_name: str) -> str:
        runtime = self._get_runtime(runtime_name, config_name)
        return runtime["name"]

    def _get_channel(self, runtime_name: str, config_name: str) -> dict:
        runtime = self._get_runtime(runtime_name, config_name)
        return runtime["channel"]

    def get_channel_type(self, runtime_name: str, config_name: str) -> str:
        channel = self._get_channel(runtime_name, config_name)
        return channel["type"]

    def get_channel_host(self, runtime_name: str, config_name: str) -> str:
        channel = self._get_channel(runtime_name, config_name)
        return channel["host"]

    def get_channel_port(self, runtime_name: str, config_name: str) -> int:
        channel = self._get_channel(runtime_name, config_name)
        return channel["port"]

    def get_modules(self, runtime_name: str, config_name: str) -> str:
        runtime = self._get_runtime(runtime_name, config_name)
        return runtime.get("modules", "")