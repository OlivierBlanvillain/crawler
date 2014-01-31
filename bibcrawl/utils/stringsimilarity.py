"""Dice's coefficient similarity function"""

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
    'HelloTest'

  @type  string: string
  @param string: the string to clean
  @rtype: string
  @return: the cleaned up string
  """
  # http://lxml.de/api/lxml.html.clean.Cleaner-class.html
  htmlCleaned = Cleaner(allow_tags=[''], remove_unknown_tags=False, style=True
      ).clean_html(string or u"dummy")
  nice = htmlCleaned[5:-6] if htmlCleaned.startswith("<div>") else htmlCleaned
  return resub(r"\s\s+" , " ", resub(r"\s\s+" , " ", nice)).strip()

def dicesCoeffSimilarity(string1, string2, bufferDict=None):
  """Computes the dice's coefficient similarity between two strings.

    >>> r = round(dicesCoeffSimilarity("Robert", "Richard"), 2)
    >>> r < round(dicesCoeffSimilarity("Robert", "Amy Robertson and co"), 2)
    True

  @type  string1: string
  @param string1: the first string
  @type  string2: string
  @param string2: the second string
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
  """Computes the similarity between two strings.

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
