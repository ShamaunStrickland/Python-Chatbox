import re
from pyspark import keyword_only  ## < 2.0 -> pyspark.ml.util.keyword_only
from pyspark.ml import Transformer
from pyspark.sql.functions import udf
from pyspark.ml.param.shared import HasInputCol, HasOutputCol, Param
from pyspark.ml.util import DefaultParamsReadable, DefaultParamsWritable, MLReadable, MLWritable
from pyspark.sql.types import StringType


class RegexSubstituter(Transformer, HasInputCol, HasOutputCol, DefaultParamsReadable, DefaultParamsWritable, MLReadable, MLWritable):

    @keyword_only
    def __init__(self, inputCol=None, outputCol=None, regexSubs=None):
        module = __import__("__main__")
        setattr(module, 'RegexSubstituter', RegexSubstituter)
        super(RegexSubstituter, self).__init__()
        self.regexSubs = Param(self, "regexSubs", "")
        self._setDefault(regexSubs={})
        kwargs = self._input_kwargs
        self.setParams(**kwargs)

    @keyword_only
    def setParams(self, inputCol=None, outputCol=None, regexSubs=None):
        kwargs = self._input_kwargs
        return self._set(**kwargs)

    def setRegex(self, value):
        self._paramMap[self.regexSubs] = value
        return self

    def getRegexsubs(self):
        return self.getOrDefault(self.regexSubs)

    def _transform(self, dataset):

        regexsubs = self.getRegexsubs()

        # user defined function to loop through each of the substitutions and apply
        # them to the passed text
        t = StringType()
        def f(text):
            for sub in regexsubs:
                text = re.sub(sub[0], sub[1], text)
            return text

        # Select the input column
        in_col = dataset[self.getInputCol()]

        # Get the name of the output column
        out_col = self.getOutputCol()

        return dataset.withColumn(out_col, udf(f, t)(in_col))