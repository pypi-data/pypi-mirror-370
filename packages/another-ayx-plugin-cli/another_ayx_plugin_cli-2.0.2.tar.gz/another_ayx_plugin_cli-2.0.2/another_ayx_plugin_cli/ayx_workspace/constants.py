# Copyright (C) 2022 Alteryx, Inc. All rights reserved.
#
# Licensed under the ALTERYX SDK AND API LICENSE AGREEMENT;
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    https://www.alteryx.com/alteryx-sdk-and-api-license-agreement
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Workspace constant definitions."""
import os
from enum import Enum
from pathlib import Path

from packaging import version


class BackendLanguage(str, Enum):
    """Installation Type of Designer."""

    Python = "python"


class TemplateToolTypes(str, Enum):
    """Template tool names."""

    Input = "input"
    MultipleInputs = "multiple-inputs"
    MultipleOutputs = "multiple-outputs"
    Optional = "optional"
    Output = "output"
    SingleInputSingleOutput = "single-input-single-output"
    MultipleInputConnections = "multi-connection-input-anchor"


class YxiInstallType(str, Enum):
    """YXI installation types."""

    USER = "user"
    ADMIN = "admin"


BACKEND_PATH = Path("backend")
AYX_WORKSPACE_JSON_PATH = Path("ayx_workspace.json")
AYX_WORKSPACE_FILES = {
    BackendLanguage.Python: [
        BACKEND_PATH / "requirements-thirdparty.txt",
        BACKEND_PATH / "requirements-local.txt",
        BACKEND_PATH / "setup.py",
        BACKEND_PATH / "ayx_plugins" / "__init__.py",
    ]
}
AYX_WORKSPACE_ARTIFACT_EXTENSIONS = {BackendLanguage.Python: ".pyz"}
AYX_CLI_INSTALL_PATH = Path(__file__).parent.parent
AYX_CLI_ASSETS_PATH = AYX_CLI_INSTALL_PATH / "assets"
AYX_CLI_TEMPLATES_PATH = AYX_CLI_ASSETS_PATH / "templates"
AYX_CLI_WORKSPACE_FILES_PATH = AYX_CLI_ASSETS_PATH / "workspace_files"
TEMPLATE_ICON_PATH = AYX_CLI_WORKSPACE_FILES_PATH / "default_package_icon.png"
AYX_CLI_UI_TEMPLATE = AYX_CLI_WORKSPACE_FILES_PATH / "ui_template"
MIN_NODE_JS_VERSION = version.parse("12.0.0")
MIN_NPM_VERSION = version.parse("6.9.0")
BUILD_CACHE_DIR = Path(".ayx_cli.cache")
YXPE_CACHE_DIR = BUILD_CACHE_DIR / "YXPE"
UI_TEMPLATE_CACHE_DIR = BUILD_CACHE_DIR / "ui_tool_template"
WORKSPACE_CONFIG_DIR = Path("configuration")
DCM_SCHEMAS_DIR = Path("DcmSchemas")
TESTS_DIR = BACKEND_PATH / "tests"
TEMPLATE_TOOL_CONFIG_DIR = os.path.join("configuration", "%(tool_name)s")
TEMPLATE_TOOL_ICON_PATH = os.path.join(TEMPLATE_TOOL_CONFIG_DIR, "icon.png")
TEMPLATE_TOOL_UI_DIR = os.path.join("ui", "%(tool_name)s")
PYPI_URL = "https://pypi.org/pypi/ayx-plugin-cli/json"
UI_GIT_REPO_URL = "https://github.com/alteryx/dev-harness.git"
UI_OUTPUT_FILES = ["app.js", "index.html", "runtime.js"]
YXI_OUTPUT_DIR = Path("build") / "yxi"
TOOL_FOLDER_VERSION_SEPARATOR = "_"
BOOTSTRAP_FILE_PATH = AYX_CLI_WORKSPACE_FILES_PATH / "yxi_bootstrap.py"
