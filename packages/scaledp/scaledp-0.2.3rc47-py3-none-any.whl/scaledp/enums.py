from enum import Enum, IntEnum


class ImageType(Enum):
    FILE = "file"
    OPENCV = "opencv"
    PIL = "pil"
    WEBP = "webp"


class Device(IntEnum):
    CPU = -1
    CUDA = 0
    CUDA_0 = 0
    CUDA_1 = 1
    CUDA_2 = 2


class PSM(IntEnum):
    AUTO = 3
    AUTO_ONLY = 2
    AUTO_OSD = 1
    CIRCLE_WORD = 9
    COUNT = 14
    OSD_ONLY = 0
    RAW_LINE = 13
    SINGLE_BLOCK = 6
    SINGLE_BLOCK_VERT_TEXT = 5
    SINGLE_CHAR = 10
    SINGLE_COLUMN = 4
    SINGLE_LINE = 7
    SINGLE_WORD = 8
    SPARSE_TEXT = 11
    SPARSE_TEXT_OSD = 12


class OEM(IntEnum):
    DEFAULT = 3
    LSTM_ONLY = 1
    TESSERACT_LSTM_COMBINED = 2
    TESSERACT_ONLY = 0


class TessLib(IntEnum):
    TESSEROCR = 0
    PYTESSERACT = 1
