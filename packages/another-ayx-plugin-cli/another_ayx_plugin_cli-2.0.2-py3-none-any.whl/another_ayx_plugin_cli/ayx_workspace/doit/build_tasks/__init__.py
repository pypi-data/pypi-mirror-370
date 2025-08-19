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
"""Alteryx CLI build tasks."""
from .create_plugin import task_create_plugin
from .create_yxi import task_create_yxi
from .generate_artifact import (
    task_generate_backend_artifact,
    task_generate_dev_backend_artifact,
    task_generate_ui_artifacts,
)
from .generate_config_files import task_generate_config_files
from .generate_tests import task_generate_tests
from .generate_ui import task__unpack_ui_tool_template, task_generate_ui
from .initialize_workspace import task_initialize_workspace
from .install_yxi import task_install_yxi

__all__ = [
    "task__unpack_ui_tool_template",
    "task_create_plugin",
    "task_create_yxi",
    "task_generate_backend_artifact",
    "task_generate_dev_backend_artifact",
    "task_generate_ui_artifacts",
    "task_generate_config_files",
    "task_generate_tests",
    "task_generate_ui",
    "task_initialize_workspace",
    "task_install_yxi",
]
