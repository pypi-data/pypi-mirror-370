import json
import logging
import traceback

from pyspark.ml import Transformer
from pyspark.ml.util import DefaultParamsReadable, DefaultParamsWritable
from pyspark.sql.functions import lit, udf

from scaledp.params import (
    HasColumnValidator,
    HasDefaultEnum,
    HasInputCol,
    HasKeepInputData,
    HasNumPartitions,
    HasOutputCol,
    HasPageCol,
    HasPathCol,
    HasPropagateExc,
)
from scaledp.schemas.Document import Document
from scaledp.schemas.ExtractorOutput import ExtractorOutput


class ExtractorError(Exception):
    pass


class BaseExtractor(
    Transformer,
    HasInputCol,
    HasOutputCol,
    HasKeepInputData,
    HasPathCol,
    DefaultParamsReadable,
    DefaultParamsWritable,
    HasNumPartitions,
    HasPageCol,
    HasColumnValidator,
    HasDefaultEnum,
    HasPropagateExc,
):

    def get_params(self):
        return json.dumps({k.name: v for k, v in self.extractParamMap().items()})

    @classmethod
    def call_extractor(cls, documents, params):
        raise NotImplementedError("Subclasses should implement this method")

    def transform_udf(self, document, params=None):
        logging.info("Run Data Extractor")
        if params is None:
            params = self.get_params()
        params = json.loads(params)
        if not isinstance(document, Document):
            document = Document(**document.asDict())
        if document.exception != "":
            return ExtractorOutput(
                path=document.path,
                data="",
                type="extractor",
                exception=document.exception,
            )
        try:

            result = self.call_extractor([document], params)
        except Exception as e:
            exception = traceback.format_exc()
            exception = f"{self.uid}: Error in data extraction: {exception}, {document.exception}"
            logging.warning(f"{self.uid}: Error in data extraction.")
            if self.getPropagateError():
                raise ExtractorError from e
            return ExtractorOutput(
                path=document.path,
                data="",
                type="detector",
                exception=exception,
            )
        return result[0]

    def _transform(self, dataset):
        params = self.get_params()
        out_col = self.getOutputCol()
        in_col = self._validate(self.getInputCol(), dataset)

        result = dataset.withColumn(
            out_col,
            udf(self.transform_udf, ExtractorOutput.get_schema())(in_col, lit(params)),
        )
        if not self.getKeepInputData():
            result = result.drop(in_col)
        return result
