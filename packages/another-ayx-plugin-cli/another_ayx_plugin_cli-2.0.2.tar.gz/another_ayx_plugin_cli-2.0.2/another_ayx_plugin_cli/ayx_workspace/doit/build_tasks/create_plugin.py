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
"""Task definition for creating plugin for the specified tool."""
import os
import shutil
from pathlib import Path
from typing import Dict

from another_ayx_plugin_cli.ayx_workspace.constants import (
    AYX_WORKSPACE_JSON_PATH,
    BackendLanguage,
    DCM_SCHEMAS_DIR,
    TEMPLATE_ICON_PATH,
    TEMPLATE_TOOL_CONFIG_DIR,
    TEMPLATE_TOOL_ICON_PATH,
    TemplateToolTypes,
)
from another_ayx_plugin_cli.ayx_workspace.models.v1 import AyxWorkspaceV1
from another_ayx_plugin_cli.ayx_workspace.template_engine import TemplateEngine


def task_create_plugin() -> Dict:
    """Create a plugin for the specified tool."""
    tool_type_choices = tuple(
        (tool_type, tool_type.value) for tool_type in TemplateToolTypes
    )

    return {
        "title": lambda task: "Create plugin",
        "actions": [
            build_backend_action(AyxWorkspaceV1.load().backend_language),
            generate_tool_configuration,
            generate_schemas_dir,
        ],
        "file_dep": [AYX_WORKSPACE_JSON_PATH],
        "params": [
            {
                "name": "tool_name",
                "long": "tool_name",
                "type": str,
                "default": "PlaceholderToolName",
            },
            {
                "name": "tool_type",
                "long": "tool_type",
                "type": str,
                "default": tool_type_choices[0][1],
                "choices": tool_type_choices,
            },
            {
                "name": "tool_config",
                "long": "tool_config",
                "type": AyxWorkspaceV1,
                "default": AyxWorkspaceV1.load(),
            },
            {
                "name": "tool_folder",
                "long": "tool_folder",
                "type": str,
                "default": "PlaceholderToolName_1_0",
            },
        ],
        "uptodate": [False],
    }


def generate_plugin_code_from_templates(
    tool_name: str, tool_config: AyxWorkspaceV1
) -> None:
    """Generate plugin code using the templating engine."""
    TemplateEngine(tool_config.backend_language).generate_plugin(tool_name, tool_config)


def build_backend_action(language: BackendLanguage) -> str:
    """Build action to create a plugin."""
    try:
        return {
            BackendLanguage.Python: " ".join(
                [
                    "another-ayx-python-sdk",
                    "create-ayx-plugin",
                    "--name",
                    "%(tool_name)s",
                    "--tool-type",
                    "%(tool_type)s",
                    "--workspace-directory",
                    '"' + os.getcwd() + '"',
                ]
            )
        }[language]
    except KeyError:
        raise NotImplementedError(f"{language} is not supported as a backend language.")


def generate_tool_configuration(tool_folder: str) -> None:
    """Generate default icons for each tool."""
    tool_config_dir = Path(".") / (
        TEMPLATE_TOOL_CONFIG_DIR % {"tool_name": tool_folder}
    )
    tool_config_dir.mkdir()

    shutil.copy(
        TEMPLATE_ICON_PATH,
        Path(".") / (TEMPLATE_TOOL_ICON_PATH % {"tool_name": tool_folder}),
    )


def generate_schemas_dir(tool_folder: str) -> None:
    """Generate DCM Schemas directory for each tool."""
    tool_schemas_dir = DCM_SCHEMAS_DIR / tool_folder
    tool_schemas_dir.mkdir()
    (tool_schemas_dir / "Connections").mkdir()
    (tool_schemas_dir / "Credentials").mkdir()
    (tool_schemas_dir / "DataSources").mkdir()
