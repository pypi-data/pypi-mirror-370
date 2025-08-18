from dataclasses import dataclass
from insight_plugin.features.connector_to_plugin.models import CreateInitBase


@dataclass(frozen=True)
class CreatePluginInit(CreateInitBase):
    pass
