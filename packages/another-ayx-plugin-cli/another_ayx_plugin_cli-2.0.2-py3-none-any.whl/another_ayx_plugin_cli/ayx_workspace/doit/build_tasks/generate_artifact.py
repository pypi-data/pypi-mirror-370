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
"""Task definition for creating a language-specific backend artifact for the workspace."""
import itertools
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, Generator, List

from another_ayx_plugin_cli.ayx_workspace.constants import (
    AYX_WORKSPACE_FILES,
    BACKEND_PATH,
    BUILD_CACHE_DIR,
    BackendLanguage,
    TEMPLATE_TOOL_UI_DIR,
    UI_OUTPUT_FILES,
)
from another_ayx_plugin_cli.ayx_workspace.models.v1 import AyxWorkspaceV1
from another_ayx_plugin_cli.node_js_helpers import NodeHelper

from doit.action import CmdAction


def generate_backend_artifact_actions(
    workspace: AyxWorkspaceV1, backend_artifact_path: Path
) -> List[Any]:
    """Generate the list of actions that generate UI and backend artifacts."""
    return [
        lambda: print(f"Creating {workspace.name}.yxi..."),
        generate_install_deps_command(
            workspace.backend_language, BUILD_CACHE_DIR, backend_artifact_path
        ),
    ]


def generate_install_deps_command(
    language: BackendLanguage, cache_dir: Path, output_path: Path
) -> List[str]:
    """Delegate call to backend's build artifact command."""
    try:
        return {
            BackendLanguage.Python: [
                "another-ayx-python-sdk",
                "install-deps",
                "--dependency-cache-dir",
                str(cache_dir.resolve()),
                "--output-path",
                str(output_path.resolve()),
            ]
        }[language]
    except KeyError:
        raise NotImplementedError(f"{language} is not supported as a backend language.")


def _ui_build_action(ui_dir: Path, tool: str) -> None:
    if not ui_dir.exists():
        print(f"Skipping UI Build for {tool}")
        return

    print(f"Building UI for {tool}")
    completed_process = NodeHelper.run_npm(
        "run",
        "build",
        cwd=ui_dir,
    )
    if completed_process.returncode != 0:
        raise RuntimeError(
            f"'npm run build' on directory {ui_dir} failed with:\n"
            f"stdout:\n{completed_process.stdout}\n\n"
            f"stderr:{completed_process.stderr}"
        )


def task_generate_ui_artifacts() -> Generator[Dict, None, None]:
    """Create ui artifact from the tools in the workspace."""
    workspace = AyxWorkspaceV1.load()
    for tool_name in map(
        lambda x: str(x.backend.tool_class_name), workspace.tools.values()
    ):
        ui_dir = Path(TEMPLATE_TOOL_UI_DIR % {"tool_name": tool_name})
        yield {
            "task_dep": ["generate_config_files"],
            "file_dep": list(
                filter(
                    lambda p: p.is_file(),
                    itertools.chain(
                        ui_dir.glob("src/**/*"), ui_dir.glob("package*.json")
                    ),
                )
            ),
            "actions": [(_ui_build_action, [ui_dir, tool_name])],
            "targets": [ui_dir / "dist" / filename for filename in UI_OUTPUT_FILES],
            "name": f"build_ui_artifacts:{tool_name}",
        }


def _build_thirdparty_deps_command(
    language: BackendLanguage, cache_dir: Path, dev_mode: bool
) -> List[str]:
    try:
        return {
            BackendLanguage.Python: [
                f"{sys.executable}",
                "-m",
                "pip",
                "install",
                "-r",
                "requirements-thirdparty.txt",
                "--upgrade",
            ]
            + ["--target", str((cache_dir / "dist").resolve())]
            if not dev_mode
            else []
        }[language]
    except KeyError:
        raise NotImplementedError(f"{language} is not supported as a backend language.")


def _install_local_python_deps(
    cwd: Path, req_file: Path, cache_dir: Path, dev: bool
) -> None:
    for line in req_file.read_text().split("\n"):
        cmd = []
        cmd.extend([f"{sys.executable}", "-m", "pip", "install"])
        cmd.extend(["-e"] if dev else [])
        cmd.extend([line, "--upgrade"])
        cmd.extend(["--target", str((cache_dir / "dist").resolve())] if not dev else [])
        subprocess.run(cmd, cwd=cwd)


def _backend_artifact_common(dev_mode: bool) -> Generator[Dict, None, None]:
    workspace = AyxWorkspaceV1.load()
    if workspace.backend_language == BackendLanguage.Python:
        tp_cmd = _build_thirdparty_deps_command(
            workspace.backend_language, BUILD_CACHE_DIR, dev_mode
        )
        yield {
            "task_dep": ["generate_config_files"],
            "file_dep": [AYX_WORKSPACE_FILES[workspace.backend_language][0]],
            "actions": [
                lambda: print("installing thirdparty dependencies"),
                CmdAction(" ".join(tp_cmd), cwd=BACKEND_PATH),
            ],
            "targets": [
                BUILD_CACHE_DIR / "dist" / "ayx_python_sdk" / "__init__.py"
                if not dev_mode
                else Path("")  # replace with dev install location
            ],
            "clean": True,
            "name": "install_thirdparty_deps",
        }

        yield {
            "task_dep": ["generate_config_files"],
            "file_dep": [AYX_WORKSPACE_FILES[workspace.backend_language][1]],
            "actions": [
                lambda: print("Installing local dependencies"),
                (
                    _install_local_python_deps,
                    [
                        BACKEND_PATH,
                        AYX_WORKSPACE_FILES[workspace.backend_language][1],
                        BUILD_CACHE_DIR,
                        dev_mode,
                    ],
                ),
            ],
            "targets": [
                BUILD_CACHE_DIR / "dist" / "ayx_plugins.egg-link"
                if dev_mode
                else BUILD_CACHE_DIR / "dist" / "ayx_plugins" / "__init__.py"
            ],
            "clean": True,
            "name": "install_local_deps",
        }


def task_generate_dev_backend_artifact() -> Generator[Dict, None, None]:
    """Create a dev-mode of the backend artifact from the tools in the workspace."""
    for task in _backend_artifact_common(True):
        yield task


def task_generate_backend_artifact() -> Generator[Dict, None, None]:
    """Create a language-specific backend artifact from the tools in the workspace."""
    for task in _backend_artifact_common(False):
        yield task
