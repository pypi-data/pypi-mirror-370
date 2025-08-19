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
"""Alteryx CLI - Main program."""
import os
import shutil
import string
import subprocess
import sys
import sysconfig
from datetime import datetime
from functools import wraps
from pathlib import Path
from typing import Any, Callable, List, Optional
from zipfile import ZipFile

from another_ayx_plugin_cli.ayx_workspace.constants import (
    AYX_WORKSPACE_JSON_PATH,
    BackendLanguage,
    TEMPLATE_TOOL_ICON_PATH,
    TOOL_FOLDER_VERSION_SEPARATOR,
    TemplateToolTypes,
    YXI_OUTPUT_DIR,
    YxiInstallType,
)
from another_ayx_plugin_cli.ayx_workspace.models.v1 import (
    AyxWorkspaceV1,
    PythonSettingsV1,
    PythonToolSettingsV1,
    ToolConfigurationV1,
    ToolSettingsV1,
    UiSettingsV1,
)
from another_ayx_plugin_cli.ayx_workspace.template_tool_settings import (
    TemplateToolSettings,
    input_settings,
    multiple_input_settings,
    multiple_output_settings,
    optional_settings,
    output_settings,
    single_input_multi_connection_multi_output_settings,
    single_input_single_output_settings,
)
from another_ayx_plugin_cli.exceptions import CliError
from another_ayx_plugin_cli.validation import CLIValidator
from another_ayx_plugin_cli.version import version as cli_version

import typer

app = typer.Typer(
    help="The Alteryx CLI for SDK Development.",
)

DODO_PATH = Path(__file__).parent / "ayx_workspace" / "doit" / "dodo.py"


def _handle_cli_errors(func: Callable) -> Callable:
    @wraps(func)
    def decorator(*args: Any, **kwargs: Any) -> Any:
        try:
            return func(*args, **kwargs)
        except CliError as e:
            typer.echo(f"ERROR: {e}".encode())
            raise typer.Exit(1)

    return decorator


@app.callback()
@_handle_cli_errors
def _validate_all(ctx: typer.Context) -> None:
    CLIValidator.check_for_updates()
    node_subcommands = ["generate-ui"]  # don't require omit_ui parameters
    workspace_subcommands = [
        "create-ayx-plugin",
        "generate-config-files",
        "generate-tests",
        "generate-ui",
        "test",
        "create-yxi",
    ]
    nonzero_tools_subcommands = ["create-yxpe", "create-yxi", "designer-install"]
    if ctx.invoked_subcommand in node_subcommands:
        CLIValidator.validate_node()
    if ctx.invoked_subcommand in workspace_subcommands + nonzero_tools_subcommands:
        CLIValidator.validate_json_exists()
    if ctx.invoked_subcommand in nonzero_tools_subcommands:
        CLIValidator.validate_nonzero_tools()


@app.command()
@_handle_cli_errors
def version() -> None:
    """Display the version of the Alteryx CLI."""
    typer.echo(f"Alteryx CLI Version: {cli_version}")


# TODO: Add help for all arguments
@app.command()
@_handle_cli_errors
def update_tool_help(
    tool_name: Optional[str] = typer.Option(
        None,
        help="Name of the tool to update help for. If not provided, updates help for all tools.",
    ),
    help_url: str = typer.Option(..., help="The new help URL to set for the tool(s)."),
    build_yxi: bool = typer.Option(
        False, help="Build YXI after updating the help URL if set to True."
    ),
) -> None:
    """Update the help URL for a specific tool or all tools in the workspace, and optionally build YXI."""
    workspace = AyxWorkspaceV1.load()

    if tool_name:
        tool_names = [tool_name]
    else:
        tool_names = list(workspace.tools.keys())

    updated_tools = 0
    for tool_key in tool_names:
        if tool_key in workspace.tools:
            workspace.tools[tool_key].configuration.help_url = help_url
            updated_tools += 1
        else:
            typer.echo(f"Tool {tool_key} not found in workspace.")

    if updated_tools > 0:
        workspace.save()
        typer.echo(f"Updated help URL for {updated_tools} tool(s).")
        if build_yxi:
            create_yxi()
    else:
        typer.echo("No tools were updated.")


@app.command()
@_handle_cli_errors
def sdk_workspace_init(
    package_name: str = typer.Option(
        ...,
        prompt="Package Name",
        help="The name of the tool package that you are creating.",
    ),
    tool_category: str = typer.Option(
        default="Python SDK Examples",
        prompt="Tool Category",
        help="The category that tools will belong to in Alteryx Designer.",
    ),
    description: str = typer.Option(
        default="",
        prompt="Description",
        help="The description of the package and use-case of its tools.",
    ),
    author: str = typer.Option(
        default="", prompt="Author", help="The author of the package."
    ),
    company: str = typer.Option(
        default="", prompt="Company", help="The company that is building the package."
    ),
    backend_language: BackendLanguage = typer.Option(
        ...,
        case_sensitive=False,
        prompt="Backend Language",
        help="The language to use for the backend of tools in the package.",
    ),
) -> None:
    """Initialize the current directory as an Alteryx SDK workspace."""
    cur_dir = Path(".")

    workspace_file_path = AYX_WORKSPACE_JSON_PATH
    configuration_directory = cur_dir / "configuration"
    build_directory = cur_dir / "build_tasks"
    dodo_file = cur_dir / "dodo.py"
    backend_directory = cur_dir / "backend"
    ui_directory = cur_dir / "ui"
    schemas_dir = cur_dir / "DCMSchemas"

    paths_to_be_created = [
        workspace_file_path,
        configuration_directory,
        dodo_file,
        build_directory,
        backend_directory,
        ui_directory,
        schemas_dir,
    ]

    existing_paths = [path for path in paths_to_be_created if path.exists()]
    if existing_paths:
        _overwrite_paths_with_prompt(existing_paths)

    workspace_model = AyxWorkspaceV1(
        name=package_name,
        tool_category=tool_category,
        package_icon_path=configuration_directory / "default_package_icon.png",
        author=author,
        company=company,
        copyright=str(datetime.now().year),
        description=description,
        ayx_cli_version=cli_version,
        backend_language=backend_language,
        backend_language_settings=PythonSettingsV1(
            python_version=sysconfig.get_python_version(),
            requirements_local_path=cur_dir / "backends" / "requirements-local.txt",
            requirements_thirdparty_path=cur_dir
            / "backends"
            / "requirements-thirdparty.txt",
        ),
        tools={},
        tool_version="1.0",
    )

    workspace_model.save()

    _run_doit(["initialize_workspace"], "Workspace initialization")

    typer.echo(f"Created Alteryx workspace in directory: {Path('.').resolve()}")
    typer.echo(f"Workspace settings can be modified in: {workspace_file_path}")

    generate_config_files()


@app.command()
@_handle_cli_errors
def generate_ui(
    tool_name: Optional[List[str]] = typer.Option(
        None,
        prompt="Tool Name",
        help="The specific tool(s) you want to generate UI components for. If no arguments are passed,"
        "UI components will be generated for all tools in this workspace"
        "(Be warned, this may take a while for multi-tool workspaces)."
        "You can specify multiple individual tools as well",
    )
) -> None:
    """Generate UI components for tools in this workspace."""
    tool_names = _check_tool_name(
        tool_name, "Attempted to generate UI for nonexistent tool"
    )
    for _tool_name in tool_names:
        _run_doit(
            ["generate_ui", "--tool_name", _tool_name],
            f"Generating UI component for {_tool_name}",
        )


@app.command()
@_handle_cli_errors
def create_ayx_plugin(
    tool_name: str = typer.Option(
        ..., prompt="Tool Name", help="Name of the tool to create."
    ),
    tool_type: TemplateToolTypes = typer.Option(
        default=TemplateToolTypes.SingleInputSingleOutput,
        prompt="Tool Type",
        help="The type of tool to generate.",
    ),
    writes_output_data: bool = typer.Option(
        default=False,
        prompt="Will this tool write output data?",
        help='For use with "Disable All Tools that Write Output" in newer versions of Designer.',
    ),
    description: str = typer.Option(
        default="",
        prompt="Description",
        help="The description of the tool to generate.",
    ),
    tool_version: str = typer.Option(
        default="1.0",
        prompt="Tool Version",
        help="The version of the tool to generate.",
    ),
    dcm_namespace: str = typer.Option(
        default="",
        prompt="DCM Namespace",
        help="Namespace to register plugin's schemas into.",
    ),
    omit_ui: bool = typer.Option(
        default=False,
        prompt="Do you want to skip generating UI component? [Default: No]",
        help="Generate a UI component for this tool",
        callback=CLIValidator.validate_node_param,
    ),
) -> None:
    """Create a new Alteryx plugin in this workspace."""
    workspace = AyxWorkspaceV1.load()

    class_name = _remove_whitespace(tool_name)

    if class_name in [
        tool.backend.tool_class_name for _, tool in workspace.tools.items()
    ]:
        raise CliError(
            f"Tool {class_name} already exists in {AYX_WORKSPACE_JSON_PATH}. Duplicate tool names are prohibited."
        )

    template_tool_settings = _get_template_tool_settings(tool_type)

    tool_configuration = ToolConfigurationV1(
        long_name=tool_name,
        description=description,
        version=tool_version,
        search_tags=[],
        icon_path=Path(".")
        / (
            TEMPLATE_TOOL_ICON_PATH
            % {
                "tool_name": str(
                    class_name
                    + TOOL_FOLDER_VERSION_SEPARATOR
                    + tool_version.replace(".", "_")
                )
            }
        ),
        input_anchors=template_tool_settings.input_anchors,
        output_anchors=template_tool_settings.output_anchors,
        help_url="https://help.alteryx.com/developer-help",
        dcm_namespace=dcm_namespace,
        writes_output_data=writes_output_data,
    )

    python_tool_settings = PythonToolSettingsV1(
        tool_module="ayx_plugins",
        tool_class_name=class_name,
    )

    tool_settings = ToolSettingsV1(
        backend=python_tool_settings,
        ui=UiSettingsV1(),
        configuration=tool_configuration,
    )

    workspace.tools[class_name] = tool_settings
    workspace.save()

    typer.echo(f"Creating {tool_type} plugin: {tool_name}")
    _run_doit(
        [
            "create_plugin",
            "--tool_name",
            class_name,
            "--tool_type",
            tool_type.value,
            "--tool_folder",
            tool_settings.get_tool_folder_name(),
        ],
        "Create plugin",
    )
    generate_config_files()
    generate_tests(tool_name=[tool_name], warn_possible_failures=False)

    if not omit_ui:
        generate_ui(tool_name=[tool_name])
    else:
        typer.echo(f"WARNING: Skipping UI component generation for {tool_name}")


def _check_tool_name(tool_name: Optional[List[str]], error_msg: str) -> List[str]:
    workspace = AyxWorkspaceV1.load()

    tool_names = tool_name or []
    workspace_tool_names = [
        _remove_whitespace(_tool_name) for _tool_name in list(workspace.tools.keys())
    ]
    for _tool_name in tool_names:
        if _remove_whitespace(_tool_name) not in workspace_tool_names:
            raise CliError(error_msg)
    return (
        workspace_tool_names
        if len(tool_names) == 0
        else [_remove_whitespace(_tool_name) for _tool_name in tool_names]
    )


@app.command()
@_handle_cli_errors
def generate_tests(
    warn_possible_failures: bool = typer.Option(True),
    tool_name: Optional[List[str]] = typer.Option(
        None,
        prompt="Tool Name",
        help="The specific tools you want to generate tests for. If no arguments are passed,"
        "tests will be generated for all tools in this workspace."
        "You can specify multiple individual tools as well.",
    ),
) -> None:
    """Generate the test files for tools in this workspace."""
    tool_names = _check_tool_name(
        tool_name, "Attempted to generate tests for nonexistent tool"
    )
    for _tool_name in tool_names:
        _run_doit(
            ["generate_tests", "--tool_name", _tool_name],
            f"Generating test files for {_tool_name}",
        )
    if warn_possible_failures:
        typer.echo(
            f"Tests for {', '.join(tool_names) if len(tool_names) > 1 else tool_names[0]} have been generated."
        )
        typer.echo(
            "Please note: Tests generated by default will need to be updated to reflect changes to plugin code."
        )


@app.command()
@_handle_cli_errors
def generate_config_files() -> None:
    """Generate the config files for the tools in this workspace."""
    _run_doit(["generate_config_files"], "Generating config files")


@app.command()
@_handle_cli_errors
def create_yxi(
    omit_ui: bool = typer.Option(False, callback=CLIValidator.validate_node_param),
) -> None:
    """Create a YXI from the tools in this workspace."""
    command = ["create_yxi"]
    if omit_ui:
        command.append("--omit_ui")
    _run_doit(command, "Creating YXI")


@app.command()
@_handle_cli_errors
def designer_install(
    install_type: YxiInstallType = typer.Option(
        YxiInstallType.USER,
        prompt="Install Type",
        help="The type of install to perform.\n"
        "\nuser -> %APPDATA%\\Alteryx\\Tools"
        "\n, admin -> %ALLUSERSPROFILE%\\Alteryx\\Tools",
    ),
    omit_ui: bool = typer.Option(False, callback=CLIValidator.validate_node_param),
    dev: bool = typer.Option(False),
) -> None:
    """Install the tools from this workspace into Alteryx Designer."""
    yxi_name = AyxWorkspaceV1.load().name
    Path(f"build/yxi/{yxi_name}.yxi").unlink(missing_ok=True)
    yxi_cmd = ["create_yxi"]
    if omit_ui:
        yxi_cmd.append("--omit-ui")
    if dev:
        yxi_cmd.append("--dev")
    _run_doit(yxi_cmd, "Creating YXI")

    install_yxi(YXI_OUTPUT_DIR.resolve() / f"{yxi_name}.yxi", install_type)
    if dev:
        shutil.rmtree("build")
    typer.echo(
        "If this is your first time installing these tools, or you have made modifications to your ayx_workspace.json file, please restart Designer for these changes to take effect."
    )


@app.command()
@_handle_cli_errors
def install_yxi(
    yxi_path: Path = typer.Option(
        ...,
        exists=True,
        file_okay=True,
        dir_okay=False,
        writable=False,
        readable=True,
        resolve_path=True,
        prompt="YXI Path",
        help="Path to the YXI file to install.",
    ),
    install_type: YxiInstallType = typer.Option(
        ...,
        prompt="Install Type",
        help="The type of install to perform.\n"
        "\nuser -> %APPDATA%\\Alteryx\\Tools"
        "\n, admin -> %ALLUSERSPROFILE%\\Alteryx\\Tools",
    ),
) -> None:
    """
    Install a YXI into Designer.

    NOTE: This command does NOT support YXI's built for the original Alteryx Python SDK.
    """
    tool_names = _get_yxi_tool_names(yxi_path)
    install_dir = _get_install_dir(install_type)

    files_to_overwrite = []
    for tool_name in tool_names:
        if (install_dir / tool_name).exists():
            files_to_overwrite.append(install_dir / tool_name)

    if files_to_overwrite:
        _overwrite_paths_with_prompt(files_to_overwrite)

    _run_doit(
        ["install_yxi", "--yxi_path", str(yxi_path), "--install_dir", str(install_dir)],
        f"Installing YXI",
    )


@app.command()
def test() -> None:
    """Run the tests command for the language in question."""
    workspace = AyxWorkspaceV1.load()
    if workspace.backend_language == BackendLanguage.Python:
        _run_command(["pytest", "backend"], "Testing")


def _get_install_dir(install_type: YxiInstallType) -> Path:
    relative_path = Path("Alteryx") / "Tools"

    if "APPDATA" not in os.environ and "ALLUSERSPROFILE" not in os.environ:
        return Path("/opt") / relative_path

    user_path = os.environ.get("APPDATA")
    admin_path = os.environ.get("ALLUSERSPROFILE")

    if user_path is None:
        raise CliError("APPDATA must be set.")
    if admin_path is None:
        raise CliError("ALLUSERSPROFILE must be set.")

    return {
        YxiInstallType.USER: Path(user_path) / relative_path,
        YxiInstallType.ADMIN: Path(admin_path) / relative_path,
    }[install_type]


def _get_yxi_tool_names(yxi_path: Path) -> List[str]:
    with ZipFile(yxi_path, "r") as yxi:
        # Assumes all directories that exist at top level of YXI will be tools
        all_dirs = set([Path(path).parent for path in yxi.namelist()])
        tool_names = set(
            [directory.parts[0] for directory in all_dirs if directory.parts]
        )

    return list(tool_names)


def _get_template_tool_settings(
    tool_type: TemplateToolTypes,
) -> TemplateToolSettings:
    """Get the template tool settings based on a tool's type."""
    tool_type_to_template_tool_settings = {
        TemplateToolTypes.Input: input_settings,
        TemplateToolTypes.MultipleInputs: multiple_input_settings,
        TemplateToolTypes.MultipleOutputs: multiple_output_settings,
        TemplateToolTypes.Optional: optional_settings,
        TemplateToolTypes.Output: output_settings,
        TemplateToolTypes.SingleInputSingleOutput: single_input_single_output_settings,
        TemplateToolTypes.MultipleInputConnections: single_input_multi_connection_multi_output_settings,
    }
    return tool_type_to_template_tool_settings[tool_type]


def _remove_whitespace(s: str) -> str:
    """Remove whitespace from a string."""
    for whitespace_char in string.whitespace:
        s = s.replace(whitespace_char, "")

    return s


def _overwrite_paths_with_prompt(paths: List[Path]) -> None:
    replace = typer.confirm(
        "\nThe following paths will be overwritten:\n"
        + ("\n".join([str(path.resolve()) for path in paths]))
        + "\n\nConfirm that it is okay to remove these paths."
    )

    if not replace:
        raise typer.Abort()

    for path in paths:
        _delete_path_and_wait_for_cleanup(path)


def _delete_path_and_wait_for_cleanup(path: Path) -> None:
    if path.is_file():
        path.unlink()
    else:
        shutil.rmtree(path)

    while path.exists():
        # Wait for OS to remove file
        pass


def _run_doit(args: List[str], step_name: str) -> None:
    # Note: if the current directory has a dodo.py file, those tasks will be executed instead of the ones in DODO_PATH
    command = [
        f"{sys.executable}",
        "-m",
        "doit",
        "--file",
        str(DODO_PATH),
        "--dir",
        str(Path(".").resolve()),
    ] + args
    typer.echo(f"[{step_name}] started")
    completed_process = _run_command(command, step_name)

    if completed_process.returncode != 0:
        if completed_process.stderr:
            err_str = completed_process.stderr.read().decode("utf-8")
        else:
            err_str = ""
        raise CliError(f"{step_name} failed with error:\n" f"stderr:\n{err_str}\n")
    typer.echo(f"[{step_name}] finished")


def _run_command(args: List[str], step_name: str) -> subprocess.Popen:
    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"

    process = subprocess.Popen(
        args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=os.getcwd(), env=env
    )

    while process.poll() is None:
        output = process.stdout
        if output:
            output_line = output.readline().decode().replace("\n", "")
            if len(output_line) > 0:
                typer.echo(f"[{step_name}] {output_line}")
        else:
            break

    return process


def main() -> None:
    """Define the main Entry point to typer."""
    app()


if __name__ == "__main__":
    main()
