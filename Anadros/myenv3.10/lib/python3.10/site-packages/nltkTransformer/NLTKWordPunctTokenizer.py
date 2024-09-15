import nltk

from pyspark import keyword_only  ## < 2.0 -> pyspark.ml.util.keyword_only
from pyspark.ml import Transformer
from pyspark.ml.param.shared import HasInputCol, HasOutputCol, Param, Params, TypeConverters
# Available in PySpark >= 2.3.0
from pyspark.ml.util import DefaultParamsReadable, DefaultParamsWritable, JavaMLReader, MLReadable, MLWritable
from pyspark.sql.functions import udf
from pyspark.sql.types import ArrayType, StringType


class NLTKWordPunctTokenizer(
    Transformer, HasInputCol, HasOutputCol,
    # Credits https://stackoverflow.com/a/52467470
    # by https://stackoverflow.com/users/234944/benjamin-manns
    DefaultParamsReadable, DefaultParamsWritable, MLReadable, MLWritable):
    stopwords = Param(Params._dummy(), "stopwords", "stopwords",
                      typeConverter=TypeConverters.toListString)

    @keyword_only
    def __init__(self, inputCol=None, outputCol=None, stopwords=None):
        super(NLTKWordPunctTokenizer, self).__init__()
        module = __import__("__main__")
        setattr(module, 'NLTKWordPunctTokenizer', NLTKWordPunctTokenizer)
        self.stopwords = Param(self, "stopwords", "")
        self._setDefault(stopwords=[])
        kwargs = self._input_kwargs
        self.setParams(**kwargs)

    @keyword_only
    def setParams(self, inputCol=None, outputCol=None, stopwords=None):
        kwargs = self._input_kwargs
        return self._set(**kwargs)

    def setStopwords(self, value):
        return self._set(stopwords=list(value))

    def getStopwords(self):
        return self.getOrDefault(self.stopwords)

    # Required in Spark >= 3.0
    def setInputCol(self, value):
        """
        Sets the value of :py:attr:`inputCol`.
        """
        return self._set(inputCol=value)

    # Required in Spark >= 3.0
    def setOutputCol(self, value):
        """
        Sets the value of :py:attr:`outputCol`.
        """
        return self._set(outputCol=value)

    def _transform(self, dataset):
        stopwords = set(self.getStopwords())

        def f(s):
            tokens = nltk.tokenize.wordpunct_tokenize(s)
            return [t for t in tokens if t.lower() not in stopwords]

        t = ArrayType(StringType())
        out_col = self.getOutputCol()
        in_col = dataset[self.getInputCol()]
        return dataset.withColumn(out_col, udf(f, t)(in_col))
