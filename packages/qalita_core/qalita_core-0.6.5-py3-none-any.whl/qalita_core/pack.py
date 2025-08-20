"""
# QALITA (c) COPYRIGHT 2025 - ALL RIGHTS RESERVED -
"""

import os
import json
import base64
import logging
from qalita_core.data_source_opener import get_data_source
from urllib.parse import urlsplit


class Pack:
    """
    Represents a pack in the system, handling configurations and data loading.
    """

    # Default configuration paths
    default_configs = {
        "pack_conf": "pack_conf.json",
        "source_conf": "source_conf.json",
        "target_conf": "target_conf.json",
        "agent_file": "~/.qalita/.agent",
    }

    def __init__(self, configs=None):
        self.logger = logging.getLogger(self.__class__.__name__)

        if configs is None:
            configs = {}

        # Update default paths with any provided configurations
        self.config_paths = {**self.default_configs, **configs}
        self.pack_config = ConfigLoader.load_config(self.config_paths["pack_conf"])
        self.source_config = ConfigLoader.load_config(self.config_paths["source_conf"])
        self.target_config = ConfigLoader.load_config(self.config_paths["target_conf"])
        self.agent_config = self.load_agent_config(self.config_paths["agent_file"])
        self.metrics = PlatformAsset("metrics")
        self.recommendations = PlatformAsset("recommendations")
        self.schemas = PlatformAsset("schemas")

        # Validate configurations
        if not self.source_config:
            self.logger.error("Source configuration is empty.")
        elif "type" not in self.source_config:
            self.logger.error("Source configuration is missing the 'type' key.")

    def load_agent_config(self, agent_file_path):
        try:
            abs_agent_file_path = os.path.expanduser(
                agent_file_path
            )  # Resolve any user-relative paths
            with open(abs_agent_file_path, "r") as agent_file:
                encoded_content = agent_file.read()
                decoded_content = base64.b64decode(encoded_content).decode("utf-8")
                data = json.loads(decoded_content)
                # Normalize local context URL to scheme://host without trailing API paths
                try:
                    local_ctx = data.get("context", {}).get("local", {})
                    original_url = local_ctx.get("url")
                    if isinstance(original_url, str) and original_url:
                        parts = urlsplit(original_url)
                        if parts.scheme and parts.netloc:
                            base_url = f"{parts.scheme}://{parts.netloc}"
                            local_ctx["url"] = base_url
                except Exception:
                    # Do not fail if normalization cannot be applied
                    pass
                return data
        except Exception as e:
            self.logger.error(f"Error loading agent configuration: {e}")
            return {}

    def load_data(self, trigger, table_or_query=None):
        source_conf = self.source_config if trigger == "source" else self.target_config
        pack_conf = self.pack_config
        ds = get_data_source(source_conf)
        table_or_query = table_or_query or source_conf.get("config", {}).get("table_or_query")
        df = ds.get_data(table_or_query, pack_config=pack_conf)
        if trigger == "source":
            self.df_source = df
            return self.df_source
        elif trigger == "target":
            self.df_target = df
            return self.df_target


class ConfigLoader:
    """Utility class for loading configuration files."""

    @staticmethod
    def load_config(file_name):
        # logger = logging.getLogger("ConfigLoader")
        try:
            with open(file_name, "r", encoding="utf-8") as file:
                return json.load(file)
        except FileNotFoundError as e:
            # logger.warning(f"Configuration file not found: {file_name}")
            return {}


class PlatformAsset:
    """
    A platform asset is a json formated data that can be pushed to the platform
    """

    def __init__(self, type):
        self.type = type
        self.data = []

    def save(self):
        # Writing data to metrics.json
        with open(self.type + ".json", "w", encoding="utf-8") as file:
            json.dump(self.data, file, indent=4)
