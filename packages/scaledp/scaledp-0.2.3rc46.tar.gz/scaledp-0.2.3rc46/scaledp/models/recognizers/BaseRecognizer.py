import json
import logging
import traceback

import pandas as pd
from pyspark.sql.functions import lit, pandas_udf, udf

from scaledp.models.recognizers.BaseOcr import BaseOcr
from scaledp.params import HasInputCols
from scaledp.schemas.DetectorOutput import DetectorOutput
from scaledp.schemas.Document import Document
from scaledp.schemas.Image import Image


class BaseRecognizer(BaseOcr, HasInputCols):

    def transform_udf(self, image, boxes, params=None):
        logging.info("Run Text Recognizer")
        if params is None:
            params = self.get_params()
        params = json.loads(params)
        if not isinstance(image, Image):
            image = Image(**image.asDict())

        if not isinstance(boxes, DetectorOutput):
            boxes = DetectorOutput(**boxes.asDict())
        if image.exception != "":
            return Document(
                path=image.path,
                text="",
                bboxes=[],
                type="text",
                exception=image.exception,
            )
        try:
            image_pil = image.to_pil()
            scale_factor = self.getScaleFactor()
            if scale_factor != 1.0:
                resized_image = image_pil.resize(
                    (
                        int(image_pil.width * scale_factor),
                        int(image_pil.height * scale_factor),
                    ),
                )
            else:
                resized_image = image_pil

            result = self.call_recognizer(
                [(resized_image, image.path)],
                [boxes],
                params,
            )
        except Exception:
            exception = traceback.format_exc()
            exception = (
                f"{self.uid}: Error in text recognition: {exception}, {image.exception}"
            )
            logging.warning(f"{self.uid}: Error in text recognition.")
            return Document(
                path=image.path,
                text="",
                bboxes=[],
                type="ocr",
                exception=exception,
            )
        return result[0]

    @classmethod
    def transform_udf_pandas(
        cls,
        images: pd.DataFrame,
        boxes: pd.DataFrame,
        params: pd.Series,
    ) -> pd.DataFrame:
        params = json.loads(params[0])
        resized_images = []
        boxes_o = []
        for (_index, img), (_, b) in zip(images.iterrows(), boxes.iterrows()):
            box = b
            image = img
            if not isinstance(image, Image):
                image = Image(**image.to_dict())
            if not isinstance(box, DetectorOutput):
                box = DetectorOutput(**box.to_dict())
            image_pil = image.to_pil()
            scale_factor = params["scaleFactor"]
            if scale_factor != 1.0:
                resized_image = image_pil.resize(
                    (
                        int(image_pil.width * scale_factor),
                        int(image_pil.height * scale_factor),
                    ),
                )
            else:
                resized_image = image_pil
            resized_images.append((resized_image, image.path))
            boxes_o.append(box)

        results = cls.call_recognizer(resized_images, boxes_o, params)

        return pd.DataFrame(results)

    @classmethod
    def call_recognizer(cls, resized_images, boxes, params):
        raise NotImplementedError("Subclasses should implement this method")

    def _transform(self, dataset):
        out_col = self.getOutputCol()
        image_col = self._validate(self.getInputCols()[0], dataset)
        box_col = self._validate(self.getInputCols()[1], dataset)
        params = self.get_params()

        if not self.getPartitionMap():
            result = dataset.withColumn(
                out_col,
                udf(self.transform_udf, Document.get_schema())(
                    image_col,
                    box_col,
                    lit(params),
                ),
            )
        else:
            if self.getNumPartitions() > 0:
                if self.getPageCol() in dataset.columns:
                    dataset = dataset.repartition(self.getPageCol())
                elif self.getPathCol() in dataset.columns:
                    dataset = dataset.repartition(self.getPathCol())
                dataset = dataset.coalesce(self.getNumPartitions())
            result = dataset.withColumn(
                out_col,
                pandas_udf(self.transform_udf_pandas, self.outputSchema())(
                    image_col,
                    box_col,
                    lit(params),
                ),
            )

        if not self.getKeepInputData():
            result = result.drop(image_col)
        return result
