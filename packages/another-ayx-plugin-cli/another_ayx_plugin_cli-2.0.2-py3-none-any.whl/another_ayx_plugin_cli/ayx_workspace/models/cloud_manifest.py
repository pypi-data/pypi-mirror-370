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
"""Pydantic model generated from platform/yxpe/manifest.schema.json."""
from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional

from pydantic import BaseModel, Field
from pydantic.types import StringConstraints

from typing_extensions import Annotated


class Author(BaseModel):
    """Author model for cloud manifest JSON."""

    name: str = Field(..., description="Author name.", title="Authors name.")
    email: Optional[str] = Field(
        None, description="Authors email address.", title="Authors email address."
    )
    company: Optional[str] = Field(
        None, description="Authors company, if any.", title="Authors company."
    )


class Support(BaseModel):
    """Support model for cloud manifest JSON."""

    email: str = Field(
        ..., description="Primary support email address.", title="Support email."
    )
    url: str = Field(
        ...,
        description="URL in which a user may find support information, documentation, etc.",
        title="Support URL.",
    )


class Runtime(BaseModel):
    """Runtime model for cloud manifest JSON."""

    command: str = Field(
        ...,
        description="Command or executable to start the plugin.",
        title="Main command.",
    )
    args: Optional[List[str]] = Field(
        None,
        description="Any argument(s) supplied to the command.",
        title="Command arguments.",
    )
    image: str = Field(
        ...,
        description="Image used to host this plugin during runtime.",
        title="Runtime image.",
    )


class Plugins(BaseModel):
    """Plugin metadata and runtime information."""

    packageName: str = Field(  # noqa: N815
        ...,
        description="A globally unique package name identifying the plugin.",
        title="Unique plugin identifier.",
        pattern=r"^[a-z][a-z0-9_]*(\.[a-z0-9_]+)+[0-9a-z_]$",
    )
    name: str = Field(
        ..., description="A friendly name for the plugin.", title="Plugin name."
    )
    description: str = Field(
        ..., description="A short, friendly description.", title="Plugin Description."
    )
    category: str = Field(
        ...,
        description="A category for which the plugin will live within.",
        title="Plugin Category.",
    )
    version: str = Field(
        ...,
        description="The semantic version of this plugin. https://semver.org/",
        title="Plugin version.",
    )
    authors: List[Author] = Field(
        ...,
        description="Information about relevant plugin author(s).",
        title="Plugin author(s).",
    )
    support: Optional[Support] = Field(
        None,
        description="Relevant information for support on this plugin.",
        title="Plugin support information.",
    )
    copyright: str = Field(
        ..., description="Plugin copyright.", title="Plugin copyright."
    )
    runtime: Runtime = Field(
        ..., description="Plugin runtime information.", title="Plugin runtime."
    )


class Engine(BaseModel):
    """Information for Engine to consume."""

    plugins: Dict[
        Annotated[str, StringConstraints(pattern=r"[A-Za-z]+[A-Za-z0-9-_]*")], Plugins
    ] = Field(
        ...,
        description="An object describing one or more plugins within this YXPE.",
        title="Plugins.",
    )


class CloudManifestSchema(BaseModel):
    """Manifest used by consumers to determine runtime configuration for a tool."""

    version: str = Field(
        ...,
        description="The semantic version of this manifest file. https://semver.org/",
        title="Manifest version.",
    )
    engine: Engine = Field(
        ...,
        description="An explanation about the purpose of this instance.",
        title="The engine schema",
    )

    def save(self, path: Path) -> None:
        """Save manifest to file."""
        with open(path, mode="w") as output_file:
            output_file.write(self.model_dump_json(indent=4))
