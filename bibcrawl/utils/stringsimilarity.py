"""Implements string similarity."""

from bibcrawl.utils.ohpython import *
from lxml.html.clean import Cleaner
from re import sub as resub

def bigrams(string):
  """Compute the bigrams (pair of adjacent characters) of a string.

    >>> bigrams("scala")
    set(['sc', 'ca', 'al', 'la'])

  @type  string: string
  @param string: the string to process
  @rtype: set of string of size two
  @return: the set of bigrams
   """
  return set(imap(lambda i: string[i : i + 2], xrange(len(string) - 1)))

def cleanTags(string):
  """Remove all html tags from the string.

    >>> cleanTags("<html><head><title>Hello</title><body>Test</body></html>")
    '<div>HelloTest</div>'

  @type  string: string
  @param string: the string to clean
  @rtype: string
  @return: the cleaned up string
  """
  # http://lxml.de/api/lxml.html.clean.Cleaner-class.html
  htmlCleaned = Cleaner(allow_tags=[''], remove_unknown_tags=False, style=True
      ).clean_html(string or u"dummy")
  return resub(r"\s\s+" , " ", resub(r"\s\s+" , " ", htmlCleaned)).strip()

def dicesCoeffSimilarity(string1, string2, bufferDict=None):
  """Computes the dice's coefficient similarity between two strings.

    >>> r = round(dicesCoeffSimilarity("Robert", "Richard"), 2)
    >>> r < round(dicesCoeffSimilarity("Robert", "Amy Robertson and co"), 2)
    True

  @type  string1: string
  @param string1: the string to clean
  @type  string2: string
  @param string2: the string to clean
  @type  bufferDict: dict
  @param bufferDict: buffer dictionary
  @rtype: float in [0;1]
  @return: the similarity of the inputs
  """
  computeBigrams = lambda _: bigrams(cleanTags(_))

  bigrams1 = getOrElseUpdate(bufferDict, string1, computeBigrams)
  bigrams2 = getOrElseUpdate(bufferDict, string2, computeBigrams)

  intersection = bigrams1.intersection(bigrams2)
  return (2.0 * len(intersection)) / (len(bigrams1) + len(bigrams2))

def stringSimilarity(string1, string2, bufferDict=None):
  """Computes similarity between two strings.

  @type  string1: string
  @param string1: the string to clean
  @type  string2: string
  @param string2: the string to clean
  @type  bufferDict: dict
  @param bufferDict: buffer dictionary
  @rtype: float in [0;1]
  @return: the similarity of the inputs
  """
  return dicesCoeffSimilarity(string1, string2, bufferDict)
  # from difflib import SequenceMatcher
  # from itertools import imap

  ## Google DMP:
  # from diff_match_patch import diff_match_patch
  # dmp = diff_match_patch()
  # dmp.Diff_Timeout = 0.1
  # diffs = dmp.diff_main(cleanTags(string1), cleanTags(string2))
  # dmp.diff_cleanupEfficiency(diffs)
  # return dmp.diff_levenshtein(diffs)

  ## Dice's coefficient similarity

  ## SequenceMatcher
  # sm = SequenceMatcher(cleanTags(string1), cleanTags(string2))
  # blocks = sm.get_matching_blocks()
  # score = sum(imap(lambda _: _.size * _.size, blocks))
  # return score
