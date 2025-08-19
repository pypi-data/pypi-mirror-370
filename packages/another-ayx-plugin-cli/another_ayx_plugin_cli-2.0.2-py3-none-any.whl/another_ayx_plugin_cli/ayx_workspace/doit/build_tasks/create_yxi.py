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
"""Task definition for creating a YXI for the workspace."""
import shutil
import site
import tempfile
from pathlib import Path
from typing import Dict, Generator

from another_ayx_plugin_cli.ayx_workspace.constants import (
    BOOTSTRAP_FILE_PATH,
    BUILD_CACHE_DIR,
    TEMPLATE_TOOL_CONFIG_DIR,
    TEMPLATE_TOOL_UI_DIR,
    WORKSPACE_CONFIG_DIR,
    YXI_OUTPUT_DIR,
)
from another_ayx_plugin_cli.ayx_workspace.models.v1 import (
    AyxWorkspaceV1,
    ManifestV1,
    ToolSettingsV1,
)
from another_ayx_plugin_cli.ayx_workspace.template_engine import TemplateEngine

from doit import task_params


@task_params(
    [
        {"name": "omit_ui", "default": False, "type": bool, "long": "omit_ui"},
        {"name": "dev", "default": False, "type": bool, "long": "dev_mode"},
    ]
)  # type: ignore
def task_create_yxi(omit_ui: bool, dev: bool) -> Generator[Dict, None, None]:
    """Create a YXI from the tools in the workspace."""
    workspace = AyxWorkspaceV1.load()
    template_engine = TemplateEngine(workspace.backend_language)

    tasks = ["generate_config_files"]
    if dev:
        tasks.append("generate_dev_backend_artifact")
    else:
        tasks.append("generate_backend_artifact")

    if not omit_ui:
        tasks.append(
            "generate_ui_artifacts"
        )  # generate_ui_artifact will only happen for plugins with a ui folder

    yield {
        "file_dep": [],
        "actions": [template_engine.generate_workspace_bootstrap],
        "targets": ["main.pyz"],
        "name": "create_workspace_bootstrap",
    }

    yield {
        "task_dep": tasks,
        "actions": [(create_yxi, [workspace, dev])],
        "targets": [YXI_OUTPUT_DIR / f"{workspace.name}.yxi"],
        "clean": True,
        "name": "create_yxi",
    }


def create_yxi(workspace: AyxWorkspaceV1, dev_mode: bool) -> None:
    """Bundle workspace tools into a yxi."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir_path = Path(temp_dir)
        copy_top_level_files(workspace, temp_dir_path)
        for index, tool in enumerate(workspace.tools.values()):
            is_ws_root = index == 0
            copy_tool(tool, temp_dir_path, is_ws_root, dev_mode)
            if dev_mode:
                manifest_path = (
                    temp_dir_path / tool.get_tool_folder_name() / "manifest.json"
                )
                manifest = ManifestV1.load(manifest_path)
                for path in site.getsitepackages():
                    manifest.additional_pythonpaths.add(path)
                manifest.save(manifest_path)

        make_archive(workspace, temp_dir_path)


def copy_top_level_files(workspace: AyxWorkspaceV1, temp_dir: Path) -> None:
    """Copy top-level config xml and icon files from workspace directory into temp directory for yxi creation."""
    top_level_config = WORKSPACE_CONFIG_DIR / "Config.xml"
    shutil.copy(top_level_config, temp_dir)
    shutil.copy(workspace.package_icon_path, temp_dir)


def create_backend_dir(target_dir: Path, dev_mode: bool) -> None:
    """Copy dist to the tool site-packages."""
    if not dev_mode:
        ws_site_packages = target_dir / "site-packages"
        shutil.copytree(BUILD_CACHE_DIR / "dist", ws_site_packages, dirs_exist_ok=True)
    shutil.copy(BOOTSTRAP_FILE_PATH, target_dir / "main.pyz")


def copy_tool(
    tool: ToolSettingsV1, temp_dir: Path, is_ws_root: bool, dev_mode: bool
) -> None:
    """Copy tool files from workspace directory into temp directory for yxi creation."""
    tool_config_dir = Path(
        TEMPLATE_TOOL_CONFIG_DIR % {"tool_name": tool.get_tool_folder_name()}
    )

    tool_schemas_dir = Path("DcmSchemas") / tool.get_tool_folder_name()

    tool_config_file = tool_config_dir / f"{tool.get_tool_folder_name()}Config.xml"
    tool_config_icon = Path(tool.configuration.icon_path).resolve()
    manifest_json = tool_config_dir / "manifest.json"
    tool_folder = temp_dir / tool.get_tool_folder_name()
    tool_folder.mkdir()
    shutil.copy(tool_config_file, tool_folder)
    if tool_schemas_dir.exists():
        shutil.copytree(
            tool_schemas_dir, tool_folder / "DcmSchemas", dirs_exist_ok=True
        )
    shutil.copy(manifest_json, tool_folder)
    shutil.copy(tool_config_icon, tool_folder)

    if is_ws_root:
        create_backend_dir(tool_folder, dev_mode)

    tool_ui_artifact_dir = Path(".") / (
        TEMPLATE_TOOL_UI_DIR % {"tool_name": tool.backend.tool_class_name}
    )
    if tool_ui_artifact_dir.is_dir():
        dist_dir = tool_ui_artifact_dir / "dist"
        if dist_dir.is_dir():
            for path in dist_dir.iterdir():
                if path.is_file() and path.suffix != ".gz":
                    shutil.copy(path, tool_folder)
        else:
            print(
                f"WARNING: {tool.backend.tool_class_name} has a ui folder, but nothing was built."
            )


def make_archive(workspace: AyxWorkspaceV1, temp_dir: Path) -> None:
    """Zip workspace and rename to yxi file."""
    YXI_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    shutil.make_archive(f"{workspace.name}.yxi", "zip", temp_dir)
    shutil.move(f"{workspace.name}.yxi.zip", YXI_OUTPUT_DIR / f"{workspace.name}.yxi")
