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
"""A module to check pypi or artifactory for CLI updates."""
from typing import Callable, Dict, List, TYPE_CHECKING, Type
from xml.etree import ElementTree

from another_ayx_plugin_cli.ayx_workspace.constants import (
    AYX_WORKSPACE_JSON_PATH,
    MIN_NODE_JS_VERSION,
    MIN_NPM_VERSION,
    PYPI_URL,
)
from another_ayx_plugin_cli.ayx_workspace.models.v1 import AyxWorkspaceV1
from another_ayx_plugin_cli.exceptions import CliError
from another_ayx_plugin_cli.node_js_helpers import NodeHelper
from another_ayx_plugin_cli.version import version as cli_version

import packaging
from packaging import version

import requests

import typer


if TYPE_CHECKING:
    import subprocess  # noqa: F401


class CLIValidator:
    """A class to validate CLI whether or not a particular CLI command should run."""

    url = PYPI_URL
    version = cli_version

    @staticmethod
    def _get_all_builds(content: str) -> List[str]:
        """Pull a list of all available ayx_cli builds from artifactory."""
        tree = ElementTree.fromstring(content)

        return list(
            sorted(
                [a.text.split("-")[1] for a in tree.iter("a") if a.text is not None],
                key=packaging.version.parse,
            )
        )

    @staticmethod
    def _get_most_recent_version_from_json(pypi_json: Dict[str, Dict[str, str]]) -> str:
        """Return the most recent ayx_cli version."""
        return pypi_json["info"]["version"]

    @classmethod
    def _get_most_recent_version_from_xml(cls, content: str) -> str:
        sorted_versions = cls._get_all_builds(content)
        return sorted_versions[-1]

    @classmethod
    def check_for_updates(cls) -> None:
        """Check to see if there's a more recent version of AyxPythonSdk available."""
        try:
            versions_page = requests.get(cls.url, timeout=10)
            versions_page.raise_for_status()
            most_recent_version = cls._get_most_recent_version_from_json(
                versions_page.json()
            )
        except (
            AttributeError,
            ValueError,
            requests.ConnectionError,
            requests.HTTPError,
            requests.Timeout,
        ):
            typer.echo(f"Can't retrieve version info from {cls.url}")
            return
        if packaging.version.parse(cls.version) < packaging.version.parse(
            most_recent_version
        ):
            typer.echo(
                f"WARNING: You are using ayx_plugin_cli version {cls.version} - Version {most_recent_version} is available"
            )

    @classmethod
    def validate_json_exists(cls) -> None:
        """Check that an 'ayx_workspace.json' file exists and is readable before attempting to load the workspace."""
        try:
            AyxWorkspaceV1.load()
        except FileNotFoundError:
            raise CliError(
                f"{AYX_WORKSPACE_JSON_PATH} not found in current directory. "
                "Did you initialize the workspace? (sdk-workspace-init)"
            )
        except Exception as e:
            raise CliError(f"Error loading ayx_workspace.json file:\n{e}")

    @classmethod
    def validate_nonzero_tools(cls) -> None:
        """Check that the workspace contains at least one tool before attempting to package a YXI."""
        workspace = AyxWorkspaceV1.load()
        if not workspace.tools:
            raise CliError("No tools in workspace. Add tools before packaging.")

    @classmethod
    def validate_node(cls) -> None:
        """Check that the correct versions of Node and NPM are installed on the system."""
        try:
            validate_node_js(MIN_NODE_JS_VERSION)
            validate_npm(MIN_NPM_VERSION)
        except NodeJsNotFoundError as e:
            package = "node"
            min_version = MIN_NODE_JS_VERSION
            if isinstance(e, NpmNotFoundError):
                package = "npm"
                min_version = MIN_NPM_VERSION

            raise CliError(
                f"{package} not found. {package} v{min_version} "
                "must be installed and available on the path."
            )
        except NodeJsVersionError as e:
            package = "node"
            if isinstance(e, NpmVersionError):
                package = "npm"

            raise CliError(
                f"Incompatible version of {package} found ({e.bad_version}). "
                f"The minimum required version is {e.min_version}."
            )

    @classmethod
    def validate_node_param(cls, omit_ui: bool) -> bool:
        """Validate node as parameter of create-ayx-plugin."""
        if not omit_ui:
            cls.validate_node()
        return omit_ui


class NodeJsNotFoundError(Exception):
    """NodeJS not found error."""

    pass


class NodeJsVersionError(Exception):
    """NodeJS Version error."""

    def __init__(self, min_version: str, bad_version: str):
        """Create a NodeJsVersionError."""
        self.min_version = min_version
        self.bad_version = bad_version


class NpmNotFoundError(NodeJsNotFoundError):
    """NPM not found error."""

    pass


class NpmVersionError(NodeJsVersionError):
    """NPM Version Error."""

    pass


def validate_node_js(min_version: version.Version) -> None:
    """Validate that node is installed with a minimum version."""
    _validate_js_package(
        NodeHelper.run_node_js, min_version, NodeJsNotFoundError, NodeJsVersionError
    )


def validate_npm(min_version: version.Version) -> None:
    """Validate that npm is installed with a minimum version."""
    _validate_js_package(
        NodeHelper.run_npm, min_version, NpmNotFoundError, NpmVersionError
    )


def _validate_js_package(
    runner: Callable[..., "subprocess.CompletedProcess"],
    min_version: version.Version,
    not_found_error: Type[NodeJsNotFoundError],
    version_error: Type[NodeJsVersionError],
) -> None:
    """Validate that JS packages are all available."""
    try:
        completed_process = runner("--version")
    except Exception:
        raise not_found_error()

    if completed_process.returncode != 0:
        raise not_found_error()

    package_version = version.parse(completed_process.stdout.decode("utf-8"))

    if package_version < min_version:
        raise version_error(str(min_version), str(package_version))
