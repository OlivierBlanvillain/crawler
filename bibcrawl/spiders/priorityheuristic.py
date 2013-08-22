import Levenshtein
from sys import maxint
from heapq import nlargest
from math import ceil
from itertools import *

class PriorityPredictor:
  """Implements a string priority predictor using a the Distance-Weighted k
  -Nearest-Neighbor classifier, as described in:
  http://ieeexplore.ieee.org/xpls/abs_all.jsp?arnumber=5408784
  This predictor can be used as an active machine learning algorithm by
  feeding it little by little with new item/score as they are discovered.
  
    >>> pp = PriorityPredictor(highPriority=lambda _: False)
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
  def __init__(self, highPriority):
    """Creates a PriorityPredictor instance.
    
    @type  highPriority: function of string => boolean
    @param highPriority: a function filtering high priority elements
    """
    self.highPriority = highPriority
    self.items = [("", 0)]
  
  def __call__(self, item):
    """Predicts the priority of an item. Running time is O(#feeds).
    
    @type  item: string
    @param item: the item to predict
    @rtype: integer
    @return: the predicted priority
    """
    if self.highPriority(item):
      return maxint
    else:
      k = min(5, int(ceil(len(self.items) / 2.0)))
      ratio = lambda (itm, _): Levenshtein.ratio(item, itm)
      getRatio = lambda _: _[1] # For the lulz.
      
      itemsZipRatio = imap(lambda _: (_, ratio(_)), self.items)
      knearestItemsZipRatio = nlargest(k, itemsZipRatio, key=getRatio)
      sumRatios = sum(imap(getRatio, knearestItemsZipRatio))
      weightedScores = imap(lambda ((_, score), ratio): ratio * score,
          knearestItemsZipRatio)
      return int(round(sum(weightedScores) / sumRatios))

  def feed(self, item, score):
    """Feeds the predictor with a new item and the associated score. It is
    perfectly fine to feed items little by little, alternating with
    prediction calls.
        
    @type  item: string
    @param item: the item to feed
    @type  scroe: integer
    @param scroe: the score of the item
    """
    if not self.highPriority(item):
      self.items.append((item, score))
