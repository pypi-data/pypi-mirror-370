from dataclasses import dataclass

from scaledp.schemas.Entity import Entity
from scaledp.utils.dataclass import map_dataclass_to_struct, register_type


@dataclass(order=True)
class NerOutput:
    path: str
    entities: list[Entity]
    exception: str
    json: str = ""

    @staticmethod
    def get_schema():
        return map_dataclass_to_struct(NerOutput)


register_type(NerOutput, NerOutput.get_schema)
