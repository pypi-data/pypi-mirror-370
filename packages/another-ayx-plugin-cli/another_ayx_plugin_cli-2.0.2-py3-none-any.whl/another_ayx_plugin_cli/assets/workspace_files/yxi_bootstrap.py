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
"""Add python library paths to the PYTHONPATH before running the tool."""
# This file was given the .pyz extension to ensure backwards compatibility with earlier versions of Designer Desktop
import json
import os
import pathlib
import site
import sys

os.environ["PYTHONUNBUFFERED"] = "1"
curr_directory = pathlib.Path(__file__).parent.resolve()
if (curr_directory / "site-packages").is_dir():
    site.addsitedir(str(curr_directory / "site-packages"))

if __name__ == "__main__":
    with open(curr_directory / "manifest.json") as f:
        try:
            manifest = json.load(f)
            if "additional_pythonpaths" in manifest.keys():
                for location in manifest["additional_pythonpaths"]:
                    site.addsitedir(location)
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(
                "The provided manifest JSON is not valid! Please double check the tools "
                "manifest.json!",
                e.doc,
                e.pos,
            )
    tool_package = sys.argv[2]
    tool_name = sys.argv[3]

    from another_ayx_python_sdk.providers.amp_provider.__main__ import start_sdk_tool_service

    print(f"ListenPort: {os.getenv('TOOL_SERVICE_ADDRESS')}")
    start_sdk_tool_service(tool_package, tool_name, os.getenv("TOOL_SERVICE_ADDRESS"))
