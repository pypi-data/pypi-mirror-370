import logging
import traceback
from types import MappingProxyType
from typing import Any

from pyspark import keyword_only
from pyspark.ml import Transformer
from pyspark.ml.util import DefaultParamsReadable, DefaultParamsWritable
from pyspark.sql.functions import udf

from scaledp.params import (
    AutoParamsMeta,
    HasColor,
    HasColumnValidator,
    HasDefaultEnum,
    HasImageType,
    HasInputCols,
    HasKeepInputData,
    HasNumPartitions,
    HasOutputCol,
    HasPageCol,
    HasPropagateExc,
    Param,
    Params,
    TypeConverters,
)
from scaledp.schemas.Box import Box
from scaledp.schemas.Image import Image

from ..enums import ImageType


class ImageCropError(Exception):
    pass


class ImageCropBoxes(
    Transformer,
    HasInputCols,
    HasOutputCol,
    HasKeepInputData,
    HasImageType,
    HasPageCol,
    DefaultParamsReadable,
    DefaultParamsWritable,
    HasColor,
    HasNumPartitions,
    HasColumnValidator,
    HasDefaultEnum,
    HasPropagateExc,
    metaclass=AutoParamsMeta,
):
    """Crop image by bounding boxes."""

    padding = Param(
        Params._dummy(),
        "padding",
        "Padding.",
        typeConverter=TypeConverters.toInt,
    )
    noCrop = Param(
        Params._dummy(),
        "noCrop",
        "Does not Crop if boxes is empty.",
        typeConverter=TypeConverters.toBoolean,
    )

    defaultParams = MappingProxyType(
        {
            "inputCols": ["image", "boxes"],
            "outputCol": "cropped_image",
            "keepInputData": False,
            "imageType": ImageType.FILE,
            "numPartitions": 0,
            "padding": 0,
            "pageCol": "page",
            "propagateError": False,
            "noCrop": True,
        },
    )

    @keyword_only
    def __init__(self, **kwargs: Any) -> None:
        super(ImageCropBoxes, self).__init__()
        self._setDefault(**self.defaultParams)
        self._set(**kwargs)

    def transform_udf(self, image, data):
        if not isinstance(image, Image):
            image = Image(**image.asDict())
        try:
            if image.exception != "":
                return Image(
                    path=image.path,
                    imageType=image.imageType,
                    data=bytes(),
                    exception=image.exception,
                )
            img = image.to_pil()
            results = []
            for b in data.bboxes:
                box = b
                if not isinstance(box, Box):
                    box = Box(**box.asDict())
                if box.width > box.height:
                    results.append(
                        img.crop(box.bbox(self.getPadding())).rotate(-90, expand=True),
                    )
                else:
                    results.append(img.crop(box.bbox(self.getPadding())))
            if self.getNoCrop() and len(results) == 0:
                raise ImageCropError("No boxes to crop")
            if len(results) == 0:
                results.append(img)

        except Exception as e:
            exception = traceback.format_exc()
            exception = f"ImageCropBoxes: {exception}, {image.exception}"
            logging.warning(exception)
            if self.getPropagateError():
                raise ImageCropError from e
            return Image(image.path, image.imageType, data=bytes(), exception=exception)
        return Image.from_pil(results[0], image.path, image.imageType, image.resolution)

    def _transform(self, dataset):
        out_col = self.getOutputCol()
        image_col = self._validate(self.getInputCols()[0], dataset)
        box_col = self._validate(self.getInputCols()[1], dataset)

        if self.getNumPartitions() > 0:
            dataset = dataset.repartition(self.getPageCol()).coalesce(
                self.getNumPartitions(),
            )
        result = dataset.withColumn(
            out_col,
            udf(self.transform_udf, Image.get_schema())(image_col, box_col),
        )

        if not self.getKeepInputData():
            result = result.drop(image_col)
        return result
