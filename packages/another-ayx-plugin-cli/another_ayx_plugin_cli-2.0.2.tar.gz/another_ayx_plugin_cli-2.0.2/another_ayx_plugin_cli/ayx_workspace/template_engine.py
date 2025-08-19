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
"""A module to provide a clean interface for the CLI's jinja templating features."""
import re
import site
from pathlib import Path
from typing import List

from another_ayx_plugin_cli.ayx_workspace.constants import (
    AYX_CLI_TEMPLATES_PATH,
    BACKEND_PATH,
    BackendLanguage,
    TESTS_DIR,
)
from another_ayx_plugin_cli.ayx_workspace.models.v1 import AyxWorkspaceV1

from jinja2 import Environment, FileSystemLoader


class _TemplateConfig:
    def __init__(
        self, output_dir: Path, input_files: List[str], output_files: List[str]
    ):
        self.output_dir = output_dir
        self.input_files = input_files
        self.output_files = output_files


class _LanguageTemplateConfig:
    def __init__(
        self,
        anchor_schema: str,
        plugin: _TemplateConfig,
        tests: _TemplateConfig,
        workspace_bootstrap: _TemplateConfig,
    ):
        self.anchor_schema = anchor_schema
        self.tests = tests
        self.plugin = plugin
        self.workspace_bootstrap = workspace_bootstrap


class TemplateEngine:
    """A class to wrap the CLI's jinja templating."""

    template_config = {
        BackendLanguage.Python: _LanguageTemplateConfig(
            anchor_schema="pa.schema([])",
            tests=_TemplateConfig(
                output_dir=TESTS_DIR,
                input_files=["clean_plugin_tests.j2", "README_tests.md"],
                output_files=["test_{file_name}.py", "README.md"],
            ),
            plugin=_TemplateConfig(
                output_dir=BACKEND_PATH,
                input_files=[
                    "plugin.j2",
                    "requirements-local.j2",
                    "requirements-thirdparty.j2",
                    "__init__.j2",
                    "setup.j2",
                ],
                output_files=[
                    "{package_name}/{file_name}.py",
                    "requirements-local.py",
                    "requirements-thirdparty.py",
                    "{package_name}/__init__.py",
                    "setup.py",
                ],
            ),
            workspace_bootstrap=_TemplateConfig(
                output_dir=Path("."),
                input_files=["workspace_bootstrap.j2"],
                output_files=["main.pyz"],
            ),
        )
    }

    def __init__(self, backend_language: BackendLanguage) -> None:
        template_dir = AYX_CLI_TEMPLATES_PATH / backend_language.value
        file_loader = FileSystemLoader(template_dir)
        self.env = Environment(loader=file_loader, autoescape=True)
        self.env.filters["snake_case"] = self.snake_case
        self.backend_language = backend_language

    @staticmethod
    def snake_case(name: str) -> str:
        """Convert a string from capitals to snake-case."""
        return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()

    def generate_workspace_bootstrap(self) -> None:
        """Generate main.pyz for workspace."""
        template_info = self.template_config[self.backend_language].workspace_bootstrap
        template = self.env.get_template(template_info.input_files[0])
        template.stream(dev_env_site_packages=site.getsitepackages()).dump(
            str((template_info.output_dir / template_info.output_files[0]).resolve())
        )

    def generate_plugin(self, tool_name: str, tool_config: AyxWorkspaceV1) -> None:
        """Generate plugin files from jinja templates."""
        template_info: _TemplateConfig = self.template_config[
            self.backend_language
        ].plugin
        if not template_info.output_dir.exists():
            (
                template_info.output_dir
                / tool_config.tools[tool_name].backend.tool_module
            ).mkdir(parents=True)

        package_name = tool_config.tools[tool_name].backend.tool_module
        plugin_class = tool_config.tools[tool_name].backend.tool_class_name
        file_class_mapping = {
            self.snake_case(plugin_name): plugin_name
            for plugin_name in tool_config.tools.keys()
        }
        python_sdk_version = "2.1.0"
        input_anchors = {
            key: self.template_config[self.backend_language].anchor_schema
            for key in tool_config.tools[tool_name].configuration.input_anchors.keys()
        }
        output_anchors = {
            key: self.template_config[self.backend_language].anchor_schema
            for key in tool_config.tools[tool_name].configuration.output_anchors.keys()
        }

        templates = [
            self.env.get_template(template) for template in template_info.input_files
        ]
        output_files = [out_file for out_file in template_info.output_files]
        for template, out_file in zip(templates, output_files):
            out_dir = template_info.output_dir
            template.stream(
                package_name=package_name,
                plugin_class=plugin_class,
                file_class_mapping=file_class_mapping,
                python_sdk_version=python_sdk_version,
                input_anchors=input_anchors,
                output_anchors=output_anchors,
                num_input_anchors=len(input_anchors),
                num_output_anchors=len(output_anchors),
            ).dump(
                str(
                    (
                        out_dir
                        / out_file.format(
                            package_name=package_name,
                            file_name=self.snake_case(plugin_class),
                        )
                    ).resolve()
                )
            )

    def generate_tests(self, tool_name: str, tool_config: AyxWorkspaceV1) -> None:
        """Generate test files from jinja templates."""
        template_info: _TemplateConfig = self.template_config[
            self.backend_language
        ].tests
        if not template_info.output_dir.exists():
            template_info.output_dir.mkdir(parents=True)
        templates = [
            self.env.get_template(template) for template in template_info.input_files
        ]
        output_files = [out_file for out_file in template_info.output_files]

        package_name = tool_config.tools[tool_name].backend.tool_module
        plugin_class = tool_config.tools[tool_name].backend.tool_class_name
        input_anchors = {
            key: self.template_config[self.backend_language].anchor_schema
            for key in tool_config.tools[tool_name].configuration.input_anchors.keys()
        }
        output_anchors = {
            key: self.template_config[self.backend_language].anchor_schema
            for key in tool_config.tools[tool_name].configuration.output_anchors.keys()
        }

        for template, out_file in zip(templates, output_files):
            out_dir = template_info.output_dir
            template.stream(
                package_name=package_name,
                plugin_class=plugin_class,
                input_anchors=input_anchors,
                output_anchors=output_anchors,
                num_input_anchors=len(input_anchors),
                num_output_anchors=len(output_anchors),
                snake_case_plugin_name=self.snake_case(plugin_class)
                + "_plugin_service",
            ).dump(
                str(
                    (
                        out_dir
                        / out_file.format(
                            package_name=package_name,
                            file_name=self.snake_case(plugin_class),
                        )
                    ).resolve()
                )
            )
