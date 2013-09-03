"""Implements string similarities."""

from lxml.html.clean import Cleaner
from diff_match_patch import diff_match_patch
from difflib import SequenceMatcher
import re

def _bigrams(string):
  """Compute the bigrams (pair of adjacent characters) of a string.

    >>> _bigrams("scala")
    set(['sc', 'ca', 'al', 'la'])

  @type  string: string
  @param string: the string to process
  @rtype: set of string of size two
  @return: the set of bigrams
   """
  return { string[i : i + 2] for i in xrange(len(string) - 1) }

def _cleanTags(string):
  """Remove all html tags from the string.

    >>> _cleanTags("<html><head><title>Hello</title><body>Test</body></html>")
    '<div>HelloTest</div>'

  @type  string: string
  @param string: the string to clean
  @rtype: string
  @return: the cleaned up string
  """
  htmlCleaned = Cleaner(allow_tags=[''], remove_unknown_tags=False
      ).clean_html(string or u"dummy")
  return re.sub(r"\s\s+" , " ", htmlCleaned)

def dicesCoeffSimilarity(string1, string2):
  """Computes the dice's coefficient similarity between two strings.

    >>> richard = round(stringSimilarity("Robert", "Richard"), 2)
    >>> richard < round(stringSimilarity("Robert", "Amy Robertson and co"), 2)
    True

  @type  string1: string
  @param string1: the string to clean
  @type  string2: string
  @param string2: the string to clean
  @rtype: float in [0;1]
  @return: the similarity of the inputs
  """
  # from Levenshtein import ratio
  # return ratio(_cleanTags(string1), _cleanTags(string2))
  bigrams1 = _bigrams(_cleanTags(string1))
  bigrams2 = _bigrams(_cleanTags(string2))
  intersection = bigrams1.intersection(bigrams2)
  return (2.0 * len(intersection)) / (len(bigrams1) + len(bigrams2))

def stringSimilarity(string1, string2):
  ## Google DMP:
  # dmp = diff_match_patch()
  # dmp.Diff_Timeout = 0.1
  # diffs = dmp.diff_main(_cleanTags(string1), _cleanTags(string2))
  # dmp.diff_cleanupEfficiency(diffs)
  # return dmp.diff_levenshtein(diffs)

  ## Dice's coefficient similarity
  return dicesCoeffSimilarity(string1, string2)

  ## SequenceMatcher
  sm = SequenceMatcher(_cleanTags(string1), _cleanTags(string2))
  blocks = sm.get_matching_blocks()
  score = sum(imap(lambda _: _.size * _.size, blocks))
  return score
