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
"""Class that sets template tool settings for different tool types."""
from typing import Dict

from another_ayx_plugin_cli.ayx_workspace.models.v1 import (
    InputAnchorV1,
    OutputAnchorV1,
)

from pydantic import BaseModel


class TemplateToolSettings(BaseModel):
    """Sets input anchors and output anchors for a tool. Used to determine default input and output anchors based on tool type."""

    input_anchors: Dict[str, InputAnchorV1]
    output_anchors: Dict[str, OutputAnchorV1]


input_settings = TemplateToolSettings(
    input_anchors={},
    output_anchors={
        "Output": OutputAnchorV1(label="", allow_multiple=False, optional=False),
    },
)
multiple_input_settings = TemplateToolSettings(
    input_anchors={
        "Input1": InputAnchorV1(label="", allow_multiple=False, optional=False),
        "Input2": InputAnchorV1(label="", allow_multiple=False, optional=False),
    },
    output_anchors={
        "Output": OutputAnchorV1(label="", allow_multiple=False, optional=False),
    },
)
multiple_output_settings = TemplateToolSettings(
    input_anchors={
        "Input": InputAnchorV1(label="", allow_multiple=False, optional=False),
    },
    output_anchors={
        "Output1": OutputAnchorV1(label="", allow_multiple=False, optional=False),
        "Output2": OutputAnchorV1(label="", allow_multiple=False, optional=False),
    },
)
optional_settings = TemplateToolSettings(
    input_anchors={
        "Input": InputAnchorV1(label="", allow_multiple=False, optional=True)
    },
    output_anchors={
        "Output": OutputAnchorV1(label="", allow_multiple=False, optional=False)
    },
)
output_settings = TemplateToolSettings(
    input_anchors={
        "Input": InputAnchorV1(label="", allow_multiple=False, optional=False)
    },
    output_anchors={},
)
single_input_single_output_settings = TemplateToolSettings(
    input_anchors={
        "Input": InputAnchorV1(label="", allow_multiple=False, optional=False)
    },
    output_anchors={
        "Output": OutputAnchorV1(label="", allow_multiple=False, optional=False)
    },
)
single_input_multi_connection_multi_output_settings = TemplateToolSettings(
    input_anchors={
        "Input": InputAnchorV1(label="", allow_multiple=True, optional=False)
    },
    output_anchors={
        "Output1": OutputAnchorV1(label="", allow_multiple=False, optional=False),
        "Output2": OutputAnchorV1(label="", allow_multiple=False, optional=False),
        "Output3": OutputAnchorV1(label="", allow_multiple=False, optional=False),
        "Output4": OutputAnchorV1(label="", allow_multiple=False, optional=False),
        "Output5": OutputAnchorV1(label="", allow_multiple=False, optional=False),
    },
)
