# Copyright (C) 2023 Alteryx, Inc. All rights reserved.
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
"""Task definition for generation of UI components."""
import shutil
import zipfile
from pathlib import Path
from typing import Dict

from another_ayx_plugin_cli.ayx_workspace.constants import (
    AYX_CLI_WORKSPACE_FILES_PATH,
    AYX_WORKSPACE_JSON_PATH,
    TEMPLATE_TOOL_UI_DIR,
    UI_TEMPLATE_CACHE_DIR,
)
from another_ayx_plugin_cli.node_js_helpers import NodeHelper

from doit import task_params
from doit.tools import run_once


def task__unpack_ui_tool_template() -> Dict:
    """Task to download the UI tool template."""
    return {
        "title": lambda task: "Download Tool Template",
        "actions": [(unpack_ui_tool_template, [UI_TEMPLATE_CACHE_DIR])],
        "targets": [UI_TEMPLATE_CACHE_DIR],
        "uptodate": [run_once],
    }


@task_params([{"name": "tool_name", "type": str, "long": "tool_name", "default": "PlaceholderToolName"}])  # type: ignore
def task_generate_ui(tool_name: str) -> Dict:
    """Task to generate UI components."""
    return {
        "title": lambda task: "Generate UI",
        "actions": [copy_ui_tool_template, ui_npm_install],
        "file_dep": [AYX_WORKSPACE_JSON_PATH],
        "task_dep": ["_unpack_ui_tool_template"],
        "targets": [
            Path(TEMPLATE_TOOL_UI_DIR % {"tool_name": tool_name}) / "package.json"
        ],
    }


def unpack_ui_tool_template(path: Path = UI_TEMPLATE_CACHE_DIR) -> None:
    """Download the UI template from github to the specified location."""
    print("Unpacking UI components")
    if path.exists():
        raise FileExistsError
    with zipfile.ZipFile(
        AYX_CLI_WORKSPACE_FILES_PATH / "ui_artifact.zip"
    ) as ui_artifact:
        ui_artifact.extractall(path)


def copy_ui_tool_template(tool_name: str) -> None:
    """Copy the UI tool template to the new tool location."""
    print("Copying cloned UI tool template")
    shutil.copytree(
        UI_TEMPLATE_CACHE_DIR,
        Path(".") / (TEMPLATE_TOOL_UI_DIR % {"tool_name": tool_name}),
    )


def ui_npm_install(tool_name: str) -> None:
    """Copy the UI tool template to the new tool location."""
    print("Installing UI components via npm")
    NodeHelper.run_npm(
        "install",
        "--legacy-peer-deps",
        cwd=Path(".") / (TEMPLATE_TOOL_UI_DIR % {"tool_name": tool_name}),
    )
