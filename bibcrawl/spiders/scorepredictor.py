"""Score predictor."""
from sys import maxint
from Levenshtein import ratio
from heapq import nlargest
from math import ceil
from itertools import imap

class ScorePredictor(object):
  """Implements a string score predictor using a the Distance-Weighted k
  -Nearest-Neighbor classifier, as described in:
  http://ieeexplore.ieee.org/xpls/abs_all.jsp?arnumber=5408784
  This predictor can be used as an active machine learning algorithm by
  feeding it little by little with new item/score as they are discovered.

    >>> pp = ScorePredictor()
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
    """Create a new ScorePredictor for a given highScore function.

    @type  highScore: function of string => boolean
    @param highScore: filter for item that should be given a very high score
    """
    self.itemsZscore = [("", 0)]
    self.highScore = highScore

  def __call__(self, item):
    """Predicts the score of an item. Running time is O(#feeds).

    @type  item: string
    @param item: the item to predict
    @rtype: integer
    @return: the predicted score
    """
    if self.highScore(item):
      return maxint
    else:
      k = min(5, int(ceil(len(self.itemsZscore) / 2.0)))
      first = lambda _: _[0] # For the lulz.

      ratioZscore = imap(lambda (i, s): (ratio(item, i), s), self.itemsZscore)
      knearestRatioZscore = nlargest(k, ratioZscore, first)
      sumRatios = sum(imap(first, knearestRatioZscore))
      weightedScores = imap(lambda (r, s): r * s, knearestRatioZscore)
      # print "    Predicted {} for url {}.".format(
      #     int(round(sum(weightedScores) / (sumRatios or 1))),
      #     item)
      return int(round(sum(weightedScores) / (sumRatios or 1)))

  def feed(self, item, score):
    """Feeds the predictor with a new item and the associated score. It is
    perfectly fine to feed itemsZscore little by little, alternating with
    prediction calls.

    @type  item: string
    @param item: the item to feed
    @type  scroe: integer
    @param scroe: the score of the item
    """
    if not self.highScore(item):
      self.itemsZscore.append((item, score))
