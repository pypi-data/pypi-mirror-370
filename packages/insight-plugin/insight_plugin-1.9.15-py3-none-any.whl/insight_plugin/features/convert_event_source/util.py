from json import JSONDecodeError

import yaml
import os
import datetime

from insight_plugin import FILE_ENCODING
from insight_plugin.features.common.plugin_spec_util import (
    PluginSpecUtil,
    PluginSpecTypes,
)
from requests import request, RequestException
from typing import Dict
from packaging.version import Version


def config_to_dict(event_source_folder):
    config_file = f"{event_source_folder}/config.yml"
    try:
        config_dict = PluginSpecUtil.get_spec_file(spec_path=config_file)
        return format_config_dict(config_dict)
    except Exception as error_message:
        print(f"Error caused when reading in the config file - {error_message}")
        raise error_message


def save_spec_to_yaml(spec_dict: Dict, output_dir):
    yaml.Dumper.ignore_aliases = lambda *args: True
    spec_yaml = yaml.dump(spec_dict, sort_keys=False, default_flow_style=False, width=256)
    spec_to_file(spec=spec_yaml, plugin_dir=output_dir)


def format_config_dict(config_dict):
    name = config_dict.get("name", "")
    title = config_dict.get("title", convert_to_title_case(name))
    vendor = "rapid7"
    sdk_version = get_runtime()
    todays_date = datetime.datetime.now().strftime("%Y-%m-%d")
    plugin_spec = {
        "plugin_spec_version": "v2",
        "extension": "plugin",
        "products": ["insightconnect"],
        "name": f'rk_{name}',
        "title": title,
        "description": config_dict.get("description", f"A cloud-to-cloud event source for {title}"),
        "version": config_dict.get("version"),
        "connection_version": config_dict.get("connection_version"),
        "supported_versions": [todays_date],
        "vendor": vendor,
        "support": vendor,
        "status": [],
        "resources": {
            "license_url": "https://github.com/rapid7/insightconnect-plugins/blob/master/LICENSE",
        },
        "tags": [title, "Cloud", "Data Collection"],
        "sdk": {"type": "slim", "version": sdk_version, "user": "nobody"},
        "cloud_ready": True,
        "hub_tags": {
            "use_cases": ["alerting_and_notifications"],
            "keywords": ["cloud_enabled"],
            "features": [],
        },
        "key_features": [f"Data processing from {title}"],
        "requirements": [],
        "troubleshooting": [],
        "links": [f"[{name}] https://extensions.rapid7.com/extension/"],
        "references": [f"[{name}] https://extensions.rapid7.com/extension/"],
        "version_history": config_dict.get("version_history", []),
        "connection": config_dict.get("connection"),
        "tasks": config_dict.get("tasks"),
    }

    return plugin_spec


def convert_to_title_case(s: str):
    words = s.replace("_", " ").replace("-", " ").split()
    capitalised_words = [word.capitalize() for word in words]
    return " ".join(capitalised_words)


def get_rapid_kit_version() -> str:
    latest_version = ""
    try:
        response = request(
            "GET", "https://artifacts.corp.rapid7.com/ui/api/v1/ui/v2/nativeBrowser/python/rapidkit", timeout=60
        )
        versions = response.json().get("data", [])
        for version in versions:
            name = version.get("name", "")
            if not name:
                continue
            if not latest_version or Version(name) > Version(latest_version):
                latest_version = name
        print(f"Setting {latest_version} as the latest version of RapidKit")
    except (RequestException, JSONDecodeError) as exception:
        print("Error occurred while trying to retrieve the RapidKit version, defaulting to latest")
        print(f"Error: {exception}")
    return latest_version


def get_runtime():
    sdk_version = "latest"
    try:
        response = request(
            "GET",
            "https://hub.docker.com/v2/repositories/rapid7/insightconnect-python-3-slim-plugin/tags",
            params={"page_size": 3, "ordering": "last_updated"},
            timeout=60,
        )
        response.raise_for_status()
        sdk_version = response.json().get("results", [])[2].get("name", "latest")
        return sdk_version
    except (RequestException, JSONDecodeError) as exception:
        print("Error caused when attempting to retrieve the latest SDK version, defaulting to latest")
        print(f"Error: {exception}")
        return sdk_version


def spec_to_file(spec: PluginSpecTypes.Spec, plugin_dir: str) -> None:
    """
    Takes the spec file object and will write it to the plugin.spec.yaml file

    :param PluginSpecTypes.Spec spec: The yaml data to be written to the file
    :param str plugin_dir: The path of the directory where the plugin.spec.yaml will be saved
    """
    with open(os.path.join(plugin_dir, "plugin.spec.yaml"), "w", encoding=FILE_ENCODING) as plugin_spec:
        plugin_spec.write(spec)  # This is formatted in JSON not YAML
