"""Score predictor."""
from bibcrawl.spiders.parseUtils import ascii
from heapq import nlargest
from itertools import imap, ifilter
from Levenshtein import ratio as stringSimilarity
from math import ceil
from sys import maxint

class PriorityHeuristic(object):
  """Implements a string score predictor using a the Distance-Weighted k
  -Nearest-Neighbor classifier, as described in:
  http://ieeexplore.ieee.org/xpls/abs_all.jsp?arnumber=5408784
  This predictor can be used as an active machine learning algorithm by
  feeding it little by little with new url/score as they are discovered.

    >>> pp = PriorityHeuristic(highScore=lambda _: _[0].isdigit())
    >>> pp("anything")
    0
    >>> pp("1/high score page!") == maxint / 2
    True
    >>> pp.feed("/category/infos/societe", ["1/", "2/", "a/", "b/"])
    >>> pp.feed("/tag/pirate", ["c/", "d/"])
    >>> pp.feed("/category/infos/windows", ["3/", "2/"])
    >>> pp.feed("/tag/futur", list())
    >>> pp.feed("/tag/kinect", ["e/"])
    >>> pp("/tag/a_tag")
    1
    >>> pp("/category/infos/category")
    155
  """
  def __init__(self, highScore):
    """Create a new PriorityHeuristic for a given highScore function.

    @type  highScore: function of string => boolean
    @param highScore: filter for url that should be given a very high score
    """
    self.urlsZscore = [(u"", 0)]
    self.highScore = highScore

  def __call__(self, url):
    """Predicts the score of an url. Running time is O(#feeds).

    @type  url: string
    @param url: the url to predict
    @rtype: integer
    @return: the predicted score
    """
    if self.highScore(url):
      # maxint made Scrapy go out of int range because of
      # REDIRECT_PRIORITY_ADJUST = +2, / 2 solves the issue.
      return maxint / 2
    else:
      k = min(5, int(ceil(len(self.urlsZscore) / 2.0)))
      first = lambda _: _[0]
      ratioZscore = imap(
          lambda (i, s): (stringSimilarity(ascii(url), ascii(i)), s),
          self.urlsZscore)
      knearestRatioZscore = nlargest(k, ratioZscore, first)
      sumRatios = sum(imap(first, knearestRatioZscore))
      weightedScores = imap(lambda (r, s): r * s, knearestRatioZscore)
      # print "    Predicted {} for url {}.".format(
      #     int(round(sum(weightedScores) / (sumRatios or 1))),
      #     url)
      return int(round(sum(weightedScores) / (sumRatios or 1)))

  def feed(self, url, links):
    """Feeds the predictor with a new url and the associated list of links. It
    is perfectly fine to feed the predictor little by little, alternating with
    prediction calls.

    @type  url: string
    @param url: the url of the page to feed
    @type  links: list of strings
    @param links: the links present on the page
    """
    if not self.highScore(url):
      score = len(links) + 99 * len(tuple(ifilter(self.highScore, links)))
      # print "got {}, panned {} on {}".format(score, self.__call__(url), url)
      self.urlsZscore.append((url, score))
