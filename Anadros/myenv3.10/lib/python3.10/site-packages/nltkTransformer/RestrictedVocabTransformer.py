from pyspark import keyword_only  ## < 2.0 -> pyspark.ml.util.keyword_only
from pyspark.ml import Transformer
from pyspark.ml.param.shared import HasInputCol, HasOutputCol, Param
from pyspark.sql.functions import udf
from pyspark.ml.util import DefaultParamsReadable, DefaultParamsWritable, MLReadable, MLWritable
from pyspark.sql.types import StringType
import re


class RestrictedVocabTransformer(Transformer, HasInputCol, HasOutputCol, DefaultParamsReadable, DefaultParamsWritable,
                                 MLReadable, MLWritable):

    @keyword_only
    def __init__(self, inputCol=None, outputCol=None, restrictedVocabGoWords=None):
        module = __import__("__main__")
        setattr(module, 'RestrictedVocabTransformer', RestrictedVocabTransformer)
        super(RestrictedVocabTransformer, self).__init__()
        self.restrictedVocabGoWords = Param(self, "restrictedVocabGoWords", "")
        self._setDefault(restrictedVocabGoWords={})
        kwargs = self._input_kwargs
        self.setParams(**kwargs)

    @keyword_only
    def setParams(self, inputCol=None, outputCol=None, restrictedVocabGoWords=None):
        kwargs = self._input_kwargs
        return self._set(**kwargs)

    def setRestrictedVocabGoWords(self, value):
        self._paramMap[self.restrictedVocabGoWords] = value
        return self

    def getRestrictedVocabGoWords(self):
        return self.getOrDefault(self.restrictedVocabGoWords)

    def _transform(self, dataset):
        restricted_vocab_go_words = self.getRestrictedVocabGoWords()

        # User defined function
        t = StringType()

        def f(original_text):
            tokens = re.split(r'(\W+)', original_text.lower())
            restricted_vocab_tokens = [t for t in tokens if t in restricted_vocab_go_words]
            return ' '.join(restricted_vocab_tokens)

        out_col = self.getOutputCol()
        in_col = dataset[self.getInputCol()]
        return dataset.withColumn(out_col, udf(f, t)(in_col))
