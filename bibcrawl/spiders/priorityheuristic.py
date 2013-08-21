import Levenshtein
from sys import maxint
from heapq import nlargest
from math import ceil
from itertools import *

class PriorityPredictor:
  """Implements a url priority predictor using a the Distance-Weighted k
  -Nearest-Neighbor classifier, as described in this paper:
  http://ieeexplore.ieee.org/xpls/abs_all.jsp?arnumber=5408784
  This predictor can be used as an active machine learning algorithm, by
  feeding it little by little with new pages/score as they are downloaded.
  
    >>> pp = PriorityPredictor(isBlogPost=lambda _: False)
    >>> pp.feed("http://korben.info/category/infos/societe", score=10)
    >>> pp.feed("http://korben.info/tag/pirate", score=0)
    >>> pp.feed("http://korben.info/category/infos/windows", score=8)
    >>> pp.feed("http://korben.info/tag/futur", score=0)
    >>> pp.feed("http://korben.info/tag/kinect", score=0)
    >>> pp("http://korben.info/tag/a_tag")
    0
    >>> pp("http://korben.info/category/infos/category")
    6
  """
  def __init__(self, isBlogPost):
    """Creates a PriorityPredictor instance.
    
    @type  isBlogPost: function of string => boolean
    @param isBlogPost: a function filtering blog posts
    """
    self.isBlogPost = isBlogPost
    self.pages = [("", 0)]
  
  def __call__(self, url):
    """Predicts priority of a url.
    
    @type  url: string
    @param url: the url to predict
    @rtype: integer
    @return: the predicted priority
    """
    if self.isBlogPost(url):
      return maxint
    else:
      getUrl = getPage = lambda _: _[0] # For the lulz.
      getScore = getRatio = lambda _: _[1]
      ratio = lambda _: Levenshtein.ratio(url, getUrl(_))
      pagesZipRatio = imap(lambda _: (_, ratio(_)), self.pages)
      k = min(5, int(ceil(len(self.pages) / 2.0)))
      knearestPagesZipRatio = nlargest(k, pagesZipRatio, key=getRatio)
      sumRatios = sum(imap(getRatio, knearestPagesZipRatio))
      weightedScores = imap(lambda _: getRatio(_) * getScore(getPage(_)),
          knearestPagesZipRatio)
      return int(round(sum(weightedScores) / sumRatios))

  def feed(self, url, score):
    """TODO <<<<<<<<------------------------------
    """
    if not self.isBlogPost(url):
      self.pages.append((url, score))
