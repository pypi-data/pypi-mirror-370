from dataclasses import dataclass
from insight_plugin.features.connector_to_plugin.models import (
    CreateInitBase,
    SchemaSpec,
)


@dataclass(frozen=True)
class CreateActionInit(CreateInitBase):
    pass


@dataclass(frozen=True)
class CreateActionsInit(CreateInitBase):
    pass


@dataclass(frozen=True)
class ActionSchemaSpec(SchemaSpec):
    action: str = ""
    description: str = ""
