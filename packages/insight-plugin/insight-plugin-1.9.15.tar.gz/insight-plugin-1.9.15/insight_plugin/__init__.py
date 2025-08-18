import os
import sys

VERSION = "1.9.15"
ROOT_DIR = os.path.dirname(
    os.path.abspath(__file__)
)  # Python module root, ex. insight-plugin/insight_plugin/
DOCKER_CMD = "docker"
FILE_ENCODING = "utf-8"
BASE_PREFIX = "icon"
BASE_MODULE = "insightconnect_plugin_runtime"
BASE_PACKAGE = "insightconnect-plugin-runtime"
KOMAND_PREFIX = "komand"
KOMAND_MODULE = "komand"

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
