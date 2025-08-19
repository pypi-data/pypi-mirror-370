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
"""Task definition for generation of tests."""
from typing import Dict

from another_ayx_plugin_cli.ayx_workspace.constants import AYX_WORKSPACE_JSON_PATH
from another_ayx_plugin_cli.ayx_workspace.models.v1 import AyxWorkspaceV1
from another_ayx_plugin_cli.ayx_workspace.template_engine import TemplateEngine


def task_generate_tests() -> Dict:
    """Generate tests for a specified tool."""
    return {
        "title": lambda task: "Generate tests",
        "actions": [generate_tests],
        "file_dep": [AYX_WORKSPACE_JSON_PATH],
        "params": [
            {
                "name": "tool_name",
                "long": "tool_name",
                "type": str,
                "default": "PlaceholderToolName",
            },
            {
                "name": "tool_config",
                "long": "tool_config",
                "type": AyxWorkspaceV1,
                "default": AyxWorkspaceV1.load(),
            },
        ],
        "uptodate": [False],
    }


def generate_tests(tool_name: str, tool_config: AyxWorkspaceV1) -> None:
    """Generate unit tests for a plugin."""
    TemplateEngine(tool_config.backend_language).generate_tests(tool_name, tool_config)
