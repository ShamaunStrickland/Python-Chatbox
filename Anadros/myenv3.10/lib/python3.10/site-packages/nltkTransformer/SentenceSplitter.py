import nltk
from pyspark import keyword_only  ## < 2.0 -> pyspark.ml.util.keyword_only
from pyspark.ml import Transformer
from pyspark.sql.functions import udf
from pyspark.ml.param.shared import HasInputCol, HasOutputCol
from pyspark.ml.util import DefaultParamsReadable, DefaultParamsWritable, MLReadable, MLWritable
from pyspark.sql.types import ArrayType, StringType
from pyspark.sql import functions as F
from nltk.tokenize import sent_tokenize


class SentenceSplitter(Transformer, HasInputCol, HasOutputCol, DefaultParamsReadable, DefaultParamsWritable, MLReadable, MLWritable):

    @keyword_only
    def __init__(self, inputCol=None, outputCol=None):
        module = __import__("__main__")
        setattr(module, 'SentenceSplitter', SentenceSplitter)
        super(SentenceSplitter, self).__init__()
        kwargs = self._input_kwargs
        self.setParams(**kwargs)

    @keyword_only
    def setParams(self, inputCol=None, outputCol=None):
        kwargs = self._input_kwargs
        return self._set(**kwargs)

    def tokenize(self, text):
        nltk.download('punkt')
        return sent_tokenize(text)

    def _transform(self, dataset):
        # User defined function to actually split the text
        text2sents = udf(lambda text: self.tokenize(text), ArrayType(StringType()))

        # Select the input column
        in_col = dataset[self.getInputCol()]

        # Get the name of the output column
        out_col = self.getOutputCol()

        return dataset.withColumn(out_col, F.explode(text2sents(in_col)))