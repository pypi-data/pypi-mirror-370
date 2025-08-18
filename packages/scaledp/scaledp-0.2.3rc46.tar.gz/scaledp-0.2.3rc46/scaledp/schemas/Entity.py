from dataclasses import dataclass

from scaledp.schemas.Box import Box
from scaledp.utils.dataclass import (
    apply_nullability,
    map_dataclass_to_struct,
    register_type,
)


@dataclass(order=True)
class Entity:
    entity_group: str
    score: float
    word: str
    start: int
    end: int
    boxes: list[Box]

    @staticmethod
    def get_schema():
        return apply_nullability(map_dataclass_to_struct(Entity), True)


register_type(Entity, Entity.get_schema)
