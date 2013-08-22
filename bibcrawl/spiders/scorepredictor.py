"""Score predictor."""
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
  itemsZipScore = [("", 0)]

  def __call__(self, item):
    """Predicts the score of an item. Running time is O(#feeds).

    @type  item: string
    @param item: the item to predict
    @rtype: integer
    @return: the predicted score
    """
    k = min(5, int(ceil(len(self.itemsZipScore) / 2.0)))
    first = lambda _: _[0] # For the lulz.

    ratioZipScore = imap(lambda (i, s): (ratio(item, i), s), self.itemsZipScore)
    knearestRatioZipScore = nlargest(k, ratioZipScore, first)
    sumRatios = sum(imap(first, knearestRatioZipScore))
    weightedScores = imap(lambda (r, s): r * s, knearestRatioZipScore)
    return int(round(sum(weightedScores) / (sumRatios or 1)))

  def feed(self, item, score):
    """Feeds the predictor with a new item and the associated score. It is
    perfectly fine to feed itemsZipScore little by little, alternating with
    prediction calls.

    @type  item: string
    @param item: the item to feed
    @type  scroe: integer
    @param scroe: the score of the item
    """
    self.itemsZipScore.append((item, score))
