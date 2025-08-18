# Description: Schema Detector Output
from dataclasses import dataclass

from scaledp.schemas.Box import Box
from scaledp.utils.dataclass import map_dataclass_to_struct, register_type


@dataclass(order=True)
class DetectorOutput:
    path: str
    type: str
    bboxes: list[Box]
    exception: str = ""

    @staticmethod
    def get_schema():
        return map_dataclass_to_struct(DetectorOutput)


register_type(DetectorOutput, DetectorOutput.get_schema)
