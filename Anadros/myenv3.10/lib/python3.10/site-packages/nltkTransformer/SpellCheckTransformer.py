import nltk
import re
from pyspark import keyword_only  ## < 2.0 -> pyspark.ml.util.keyword_only
from pyspark.ml import Transformer
from pyspark.ml.param.shared import HasInputCol, HasOutputCol, Param
from pyspark.sql.functions import udf
from pyspark.ml.util import DefaultParamsReadable, DefaultParamsWritable, MLReadable, MLWritable
from pyspark.sql.types import StringType


class SpellCheckTransformer(Transformer, HasInputCol, HasOutputCol, DefaultParamsReadable, DefaultParamsWritable,
                            MLReadable, MLWritable):

    @keyword_only
    def __init__(self, inputCol=None, outputCol=None, restrictedVocabGoWords=None):
        module = __import__("__main__")
        setattr(module, 'SpellCheckTransformer', SpellCheckTransformer)
        super(SpellCheckTransformer, self).__init__()
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

    @staticmethod
    def _known_mispelling_correction(original_word):
        """
        Checks word against a list of know spellings and returns correction if known
        :param original_word: word to check
        :return: corrected word (if any)
        """

        # This is a list of mispellings that we directly correct
        hardcoded_corrections = dict(
            known_misspelling=[
                'ild',
                'miid',
                'mil',
                'mld',
                'mildy',
                'midly',
                'mildlt',
                'mildy',
                'sever',
                'severee',
                'severly',
                'sigificant',
                'signficant',
                'trival'
            ],
            corrected_word=[
                'mild',
                'mild',
                'mild',
                'mild',
                'mildly',
                'mildly',
                'mildly',
                'mildly',
                'severe',
                'severe',
                'severely',
                'significant',
                'significant',
                'trivial'
            ])

        # Check for match in hardcoded corrects
        for idx, known_misspelling in enumerate(hardcoded_corrections["known_misspelling"]):
            if original_word == known_misspelling:
                return hardcoded_corrections["corrected_word"][idx]

        return ''

    @staticmethod
    def _levenshtein(s, t):
        """
        Determines how different two strings are based on the levenshtein algorithm
        Algorithm retrieved from
         https://en.wikibooks.org/wiki/Algorithm_Implementation/Strings/Levenshtein_distance#Python
        which claims to be based on a version of the algorithm described in the Levenshtein wikipedia article

        :param s: string 1
        :param t: string 2
        :return:  levenshtein edit distance
        """

        if s == t:
            return 0
        elif len(s) == 0:
            return len(t)
        elif len(t) == 0:
            return len(s)
        v0 = [None] * (len(t) + 1)
        v1 = [None] * (len(t) + 1)
        for i in range(len(v0)):
            v0[i] = i
        for i in range(len(s)):
            v1[0] = i + 1
            for j in range(len(t)):
                cost = 0 if s[i] == t[j] else 1
                v1[j + 1] = min(v1[j] + 1, v0[j + 1] + 1, v0[j] + cost)
            for j in range(len(v0)):
                v0[j] = v1[j]

        return v1[len(t)]

    def _levenshtein_correction(self, original_word, restricted_vocab):
        """
        Uses levenshtein edit distance to spell correct a small number of works
        :rtype: str
        :param original_word: original word including spellings if any
        :return: corrected word (if correction necessary and found)
        """

        # No need to further check if the word already matches a keyword
        if original_word in restricted_vocab:
            return None

        # If not check and see if the word is a misspelling of a commonly mispelled important word
        correctly_spelled_easy_words = ['moderate', 'moderately', 'mitral']
        correctly_spelled_hard_words = ['regurgitation', 'regurgitant']
        correctly_spelled_words = correctly_spelled_easy_words + correctly_spelled_hard_words

        # Find if the original word is similar to any of the checked words and if it is similar return the
        # closest match
        closest_match_distance = 100  # type: int
        corrected_spelling = None

        # Loop through each of the words we're checking against
        for correctly_spelled_word in correctly_spelled_words:

            # Get the edit distance from the provided word to the correctly spelled word
            dist = self._levenshtein(original_word, correctly_spelled_word)

            # If we match a correctly spelled word exit
            if dist == 0:
                return None

            # If we are within 1 of a correctly spelled word
            if dist <= 1:
                return correctly_spelled_word

            # If we are within 2 or 3 of a word that is difficult to spell, look for the best match
            if (dist <= 3) and (correctly_spelled_word in correctly_spelled_hard_words):
                if dist < closest_match_distance:
                    closest_match_distance = dist
                    corrected_spelling = correctly_spelled_word

        # If we get here, either we will have found that the passed word is with 3 edits of a correctly spelled
        # key word or we didn't find a match and the value for the corrected spelling will be None
        return corrected_spelling

    def _get_spellcorrected_text(self, original_text, restricted_vocab):
        """
        Takes original text and returns spellchecked and corrected (if necessary) version
        :param original_text:
        :return: spellchecked and corrected sentence
        """

        # split sentence into words
        text_tokens = re.split(r'(\W+)', original_text.lower())

        # Loop through the tokens looking for errors
        for idx, token in enumerate(text_tokens):

            # check against known mispelling list
            corrected_spelling = self._known_mispelling_correction(token)
            if corrected_spelling:
                text_tokens[idx] = corrected_spelling
                continue

            # check for spelling errors using levenstein distance
            corrected_spelling = self._levenshtein_correction(token, restricted_vocab)
            if corrected_spelling:
                text_tokens[idx] = corrected_spelling

        # Stitch the tokens back together to form a string.  Note: there is no space between the
        # single quote below.  This is important because I want to put the string back together exactly as I found it
        # including and gobbldy gook inter word stuff we're splitting on.
        # This helps in the future for highlighting phrases with mispellings
        return ''.join(text_tokens)

    def _transform(self, dataset):
        restricted_vocab_go_words = self.getRestrictedVocabGoWords()

        # User defined function
        t = StringType()

        def f(original_text):
            return self._get_spellcorrected_text(original_text, restricted_vocab_go_words)

        out_col = self.getOutputCol()
        in_col = dataset[self.getInputCol()]
        return dataset.withColumn(out_col, udf(f, t)(in_col))
