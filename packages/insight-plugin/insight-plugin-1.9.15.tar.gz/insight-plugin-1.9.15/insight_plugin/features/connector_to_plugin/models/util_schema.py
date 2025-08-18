from dataclasses import dataclass
from insight_plugin.features.connector_to_plugin.models import CreateInitBase


@dataclass(frozen=True)
class CreateUtilInit(CreateInitBase):
    pass
