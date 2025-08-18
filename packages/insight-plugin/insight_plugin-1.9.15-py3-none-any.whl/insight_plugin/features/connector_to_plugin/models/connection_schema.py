from dataclasses import dataclass, field
from typing import Any, Dict
from insight_plugin.features.connector_to_plugin.models import (
    CreateInitBase,
    SchemaSpec,
)


@dataclass(frozen=True)
class CreateConnectionInit(CreateInitBase):
    pass


@dataclass(frozen=True)
class ConnectionSchemaSpec(SchemaSpec):
    connection: Dict[str, Any] = field(default_factory=dict)
