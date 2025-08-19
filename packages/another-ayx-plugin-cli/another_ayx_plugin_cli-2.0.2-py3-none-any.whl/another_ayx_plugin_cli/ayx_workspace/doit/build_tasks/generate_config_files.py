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
"""Task definition for generation of config files."""
import os
from pathlib import Path
from typing import Dict, Generator, List, Tuple

from another_ayx_plugin_cli.ayx_workspace.constants import (
    AYX_WORKSPACE_JSON_PATH,
    WORKSPACE_CONFIG_DIR,
)
from another_ayx_plugin_cli.ayx_workspace.models.cloud_manifest import (
    Author,
    CloudManifestSchema,
    Engine,
    Plugins,
    Runtime,
    Support,
)
from another_ayx_plugin_cli.ayx_workspace.models.v1 import (
    AyxWorkspaceV1,
    ManifestV1,
    ToolSettingsV1,
)

from another_ayx_plugin_cli.version import short_version

import xmltodict

CONFIG_XML_NAME = "Config.xml"


def task_generate_config_files() -> Generator[Dict, None, None]:
    """Generate the config files for the workspace."""
    yield {
        "name": "generate_config_xml",
        "targets": [WORKSPACE_CONFIG_DIR / CONFIG_XML_NAME],
        "file_dep": [AYX_WORKSPACE_JSON_PATH],
        "actions": [generate_config_xml],
        "clean": True,
        "verbosity": 2,
    }
    workspace = AyxWorkspaceV1.load()

    if workspace.tools:
        tools = workspace.tools
        (
            tool_config_xml_targets,
            manifest_json_targets,
            icon_file_targets,
        ) = generate_targets(tools)

        yield {
            "name": "generate_tool_config_xml",
            "targets": tool_config_xml_targets,
            "file_dep": [AYX_WORKSPACE_JSON_PATH],
            "actions": [generate_tool_xmls],
            "clean": True,
            "verbosity": 2,
        }

        yield {
            "name": "generate_manifest_jsons",
            "targets": manifest_json_targets,
            "file_dep": [AYX_WORKSPACE_JSON_PATH],
            "actions": [generate_manifest_jsons],
            "clean": True,
            "verbosity": 2,
        }


def generate_config_xml() -> None:
    """Parse the ayx_workspace.json to generate the top-level Config XML."""
    print("Generating top level config XML file...")
    workspace = AyxWorkspaceV1.load()
    config_xml = {
        "AlteryxJavaScriptPlugin": {
            #  TODO: Figure out what values to use for @EngineDLL and @SDKVersion -- hard coded for now
            "EngineSettings": {"@EngineDLL": "Python", "@SDKVersion": "10.1"},
            "Properties": {
                "MetaInfo": {
                    "Name": workspace.name,
                    "RootToolName": workspace.name,
                    "Description": workspace.description,
                    "CategoryName": workspace.tool_category,
                    "ToolVersion": workspace.tool_version,
                    "DcmNamespace": "",
                    "Author": workspace.author,
                    "Company": workspace.company,
                    "Copyright": workspace.copyright,
                    "Icon": Path(workspace.package_icon_path).name,
                }
            },
        }
    }

    config_xml_path = WORKSPACE_CONFIG_DIR / CONFIG_XML_NAME
    _output_dict_to_xml(config_xml, config_xml_path)


def generate_tool_xmls() -> None:
    """Parse the ayx_workspace.json to generate the tool config XMLs for each tool that is specified in the workspace json."""
    print("Generating tool configuration XMLs...")

    workspace = AyxWorkspaceV1.load()
    tools = workspace.tools
    for _, tool in tools.items():
        tool_name = tool.backend.tool_class_name

        print(f"Generating {tool_name} XML...")
        os.makedirs(WORKSPACE_CONFIG_DIR / tool.get_tool_folder_name(), exist_ok=True)

        tool_config = tool.configuration
        input_anchors = tool_config.input_anchors
        output_anchors = tool_config.output_anchors
        input_connections_dict = {}
        output_connections_dict = {}
        if input_anchors:
            input_connections_dict = _create_connection_dict(input_anchors)

        if output_anchors:
            output_connections_dict = _create_connection_dict(output_anchors)

        config_xml = {
            "AlteryxJavaScriptPlugin": {
                "EngineSettings": {
                    "@EngineDll": "SdkEnginePlugin.dll",
                    "@EngineDllEntryPoint": "SdkEnginePlugin",
                    "@SDKVersion": "10.1",
                },
                "SdkSettings": {
                    "@Manifest": "True",
                    "@Language": "Python",
                    "CustomParameters": {
                        "Version": {"@Value": short_version},
                        "ToolVersion": {"@Value": tool_config.version},
                        "WritesOutputData": {"@Value": tool_config.writes_output_data},
                    },
                },
                "GuiSettings": {
                    "@Html": "index.html",
                    "@Icon": tool_config.icon_path.name,
                    "@SDKVersion": "10.1",
                    "@Help": tool_config.help_url,
                    "InputConnections": input_connections_dict,
                    "OutputConnections": output_connections_dict,
                },
                "Properties": {
                    "MetaInfo": {
                        "Name": tool_config.long_name,
                        "RootToolName": tool_config.long_name,
                        "Description": tool_config.description,
                        "ToolVersion": tool_config.version,
                        "DcmNamespace": tool_config.dcm_namespace,
                        "CategoryName": workspace.tool_category,
                        "SearchTags": ", ".join(tool_config.search_tags),
                        "Author": workspace.author,
                        "Company": workspace.company,
                        "Copyright": workspace.copyright,
                    }
                },
            }
        }

        config_xml_path = (
            WORKSPACE_CONFIG_DIR
            / tool.get_tool_folder_name()
            / f"{tool.get_tool_folder_name()}Config.xml"
        )
        _output_dict_to_xml(config_xml, config_xml_path)

    print("Done!")


def generate_desktop_manifest(
    python_version: str, tool_name: str, entrypoint: str, tool_folder_name: str
) -> None:
    """Generate a manifest file for Designer Desktop."""
    print(f"Generating manifest.json for {tool_name}...")
    manifest = ManifestV1(
        version=python_version,
        entry_point=Path(entrypoint) / f"main.pyz",
        tool_package="ayx_plugins",
        tool_name=tool_name,
        additional_pythonpaths=[],
    )
    manifest_json_path = WORKSPACE_CONFIG_DIR / tool_folder_name / "manifest.json"
    manifest.save(manifest_json_path)


def generate_cloud_manifest(
    tool_name: str, workspace: AyxWorkspaceV1, tool: ToolSettingsV1
) -> Plugins:
    """Generate a cloud-manifest class."""
    print(f"Generating cloud_manifest.json for {tool_name}...")
    plugin = Plugins(
        packageName="com.mycompany.mytool",
        name=tool_name,
        description=tool.configuration.description,
        category=workspace.tool_category,
        version="1.0",  # TODO: logic to determine semver
        copyright=workspace.copyright,
        authors=[Author(name=workspace.author)],
        support=Support(email="email@mycompany.com", url="https://www.myscompany.com"),
        runtime=_get_runtime_from_language(
            workspace.backend_language,
            workspace.backend_language_settings.python_version,
            tool_name,
        ),
    )
    return plugin


def generate_cloud_manifest_file(
    plugins_dict: Dict[str, Plugins], tool_name: str
) -> None:
    """Generate a cloud-manifest file."""
    engine = Engine(plugins=plugins_dict)
    cloud_manifest = CloudManifestSchema(
        version="1.0", engine=engine  # TODO: logic to determine semver
    )
    cloud_manifest_json_path = WORKSPACE_CONFIG_DIR / tool_name / "cloud_manifest.json"
    cloud_manifest.save(cloud_manifest_json_path)


def generate_manifest_jsons() -> None:
    """Parse the ayx_workspace.json to generate the manifest.json that corresponds to each tool."""
    workspace = AyxWorkspaceV1.load()
    tools = workspace.tools

    entrypoint = tools[list(tools.keys())[0]].get_tool_folder_name()
    for _, tool in tools.items():
        generate_desktop_manifest(
            workspace.backend_language_settings.python_version,
            tool.backend.tool_class_name,
            entrypoint,
            tool.get_tool_folder_name(),
        )

    print("Done!")


def _get_runtime_from_language(
    language: str, python_version: str, tool_name: str
) -> Runtime:
    runtimes = {
        "python": Runtime(
            command="python",
            args=[
                "/extension/main.pyz",
                "start-sdk-tool-service",
                "ayx_plugins",
                tool_name,
                "--sdk-engine-server-address",
                "{TOOL_SERVER_ADDRESS}",
            ],
            image=f"ayx-python-{python_version}",
        )
    }
    return runtimes[language]


def _create_connection_dict(anchor_dict: Dict) -> Dict[str, List]:
    connections_dict: Dict[str, List] = {"Connection": []}
    for anchor in anchor_dict:
        connection_dict = {
            "@AllowMultiple": "True" if anchor_dict[anchor].allow_multiple else "False",
            "@Label": anchor_dict[anchor].label or "",
            "@Name": anchor,
            "@Optional": "True" if anchor_dict[anchor].optional else "False",
            "@Type": "Connection",
        }
        connections_dict["Connection"].append(connection_dict)
    return connections_dict


def generate_targets(
    tools: Dict[str, ToolSettingsV1],
) -> Tuple[List[Path], List[Path], List[Path]]:
    """Generate doit targets for subtasks."""
    tool_config_xml_targets = []
    manifest_json_targets = []
    icon_path_targets = []

    for _, tool in tools.items():
        tool_folder_name = tool.get_tool_folder_name()
        config_file_name = tool_folder_name + CONFIG_XML_NAME
        target_path = WORKSPACE_CONFIG_DIR / tool_folder_name / config_file_name
        tool_config_xml_targets.append(target_path)
        manifest_json_targets.append(
            WORKSPACE_CONFIG_DIR / tool_folder_name / "manifest.json"
        )
        manifest_json_targets.append(
            WORKSPACE_CONFIG_DIR / tool_folder_name / "cloud_manifest.json"
        )
        icon_path_targets.append(tool.configuration.icon_path)

    return tool_config_xml_targets, manifest_json_targets, icon_path_targets


def _add_xml_comment(file_path: Path) -> None:
    with open(file_path, mode="r") as generated_xml:
        lines = generated_xml.readlines()
        lines.insert(
            1, "<!--FILE AUTOMATICALLY GENERATED BY AYX_CLI. DO NOT MODIFY.-->\n"
        )
        generated_xml = open(file_path, mode="w")
        generated_xml.writelines(lines)


def _output_dict_to_xml(xml: Dict, xml_path: Path) -> None:
    with open(xml_path, mode="w") as output_file:
        xmltodict.unparse(
            xml, output=output_file, short_empty_elements=True, pretty=True
        )
        _add_xml_comment(xml_path)
