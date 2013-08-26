"""Score predictor."""
from heapq import nlargest
from itertools import imap, ifilter
from Levenshtein import ratio
from math import ceil
from sys import maxint

class PriorityHeuristic(object):
  """Implements a string score predictor using a the Distance-Weighted k
  -Nearest-Neighbor classifier, as described in:
  http://ieeexplore.ieee.org/xpls/abs_all.jsp?arnumber=5408784
  This predictor can be used as an active machine learning algorithm by
  feeding it little by little with new url/score as they are discovered.

    >>> pp = PriorityHeuristic()
    >>> pp("anything")
    0
    >>> pp.feed("/category/infos/societe", score=10)
    >>> pp.feed("/tag/pirate", score=0)
    >>> pp.feed("/category/infos/windows", score=8)
    >>> pp.feed("/tag/futur", score=0)
    >>> pp.feed("/tag/kinect", score=1)
    >>> pp("/tag/a_tag")
    0
    >>> pp("/category/infos/category")
    7
  """
  def __init__(self, highScore):
    """Create a new PriorityHeuristic for a given highScore function.

    @type  highScore: function of string => boolean
    @param highScore: filter for url that should be given a very high score
    """
    self.urlsZscore = [("", 0)]
    self.highScore = highScore

  def __call__(self, url):
    """Predicts the score of an url. Running time is O(#feeds).

    @type  url: string
    @param url: the url to predict
    @rtype: integer
    @return: the predicted score
    """
    if self.highScore(url):
      return maxint
    else:
      k = min(10, int(ceil(len(self.urlsZscore) / 2.0)))
      first = lambda _: _[0] # For the lulz.

      ratioZscore = imap(lambda (i, s): (ratio(url, i), s), self.urlsZscore)
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
      print "got {}, panned {} on {}".format(score, self.__call__(url), url)
      self.urlsZscore.append((url, score))
