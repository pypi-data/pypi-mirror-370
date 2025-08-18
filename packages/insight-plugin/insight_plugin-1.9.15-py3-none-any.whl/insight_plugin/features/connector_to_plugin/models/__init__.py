from abc import ABC
from dataclasses import dataclass, field
from typing import Any, Dict, List, Union

from insight_plugin.features.common.plugin_spec_util import PluginSpecTypes


@dataclass(frozen=True)
class CreateInitBase(ABC):
    template_filename: str
    target_dir_name: str
    inputs: Dict[str, Union[str, List[str]]] = field(default_factory=dict)


@dataclass(frozen=True)
class SchemaSpec(ABC):
    spec: PluginSpecTypes.Spec
    input: Dict[str, Any] = field(default_factory=dict)
    output: Dict[str, Any] = field(default_factory=dict)
