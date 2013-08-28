"""Dice's coefficient string similarity."""

from lxml.html.clean import Cleaner

def _bigrams(string):
  """Compute the bigrams of a string.

    >>> _bigrams("test")
    set(['te', 'es', 'st'])

  @type  page: string
  @param page: the string to process
  @rtype: set of string of size two
  @return: the set of bigrams
   """
  return { string[i:i+2] for i in xrange(len(string) - 1) }

def _cleanTags(string):
  """Remove all html tags from the string.

    >>> _cleanTags("<html><head><title>Hello</title><body>Test</body></html>")
    '<div>HelloTest</div>'

  @type  page: string
  @param page: the string to clean
  @rtype: string
  @return: the cleaned up string
  """
  cleaner = Cleaner(allow_tags=[''], remove_unknown_tags=False)
  return cleaner.clean_html(string or u"dummy")

def stringSimilarity(string1, string2):
    """Computes the dice's coefficient similarity between two strings.

      >>> round(stringSimilarity("Robert", "Richard"), 2)
      0.52
      >>> round(stringSimilarity("Robert", "Amy Robertson and co"), 2)
      0.67
      >>> from Levenshtein import ratio
      >>> round(ratio("Robert", "Richard"), 2)
      >>> round(ratio("Robert", "Amy Robertson and co"), 2)

    @type  string1: string
    @param string1: the string to clean
    @type  string2: string
    @param string2: the string to clean
    @rtype: float in [0;1]
    @return: the similarity of the inputs
    """
    # Slower and more accurate:
    # return Levenshtein.ratio(_cleanTags(string1), _cleanTags(string1))
    bigrams1 = _bigrams(_cleanTags(string1))
    bigrams2 = _bigrams(_cleanTags(string2))
    intersection = bigrams1.intersection(bigrams2)
    return (2.0 * len(intersection)) / (len(bigrams1) + len(bigrams2))
