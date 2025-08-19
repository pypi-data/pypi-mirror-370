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
"""Doit configuration file."""
from another_ayx_plugin_cli.ayx_workspace.constants import (
    AYX_WORKSPACE_JSON_PATH,
    BUILD_CACHE_DIR,
)

import doit

if AYX_WORKSPACE_JSON_PATH.exists():
    from another_ayx_plugin_cli.ayx_workspace.doit.build_tasks import *  # noqa
else:
    from another_ayx_plugin_cli.ayx_workspace.doit.build_tasks import task_install_yxi  # noqa


dep_file = (BUILD_CACHE_DIR / ".doit.db").resolve()
dep_file.parent.mkdir(exist_ok=True, parents=True)

DOIT_CONFIG = {
    "default_tasks": [],
    "dep_file": str(dep_file),
    "verbosity": 2,
    "cleanforget": True,
    "num_process": 1,
    "par_type": "thread",
}

if __name__ == "__main__":
    doit.run(globals())
