"""EvalCrawl"""

from bibcrawl.model.postitem import PostItem
from bibcrawl.utils.priorityheuristic import PriorityHeuristic
from bibcrawl.utils.ohpython import *
from bibcrawl.utils.parsing import buildUrlFilter, parseHTML
from bibcrawl.utils.parsing import extractLinks
from scrapy.http import Request
from bibcrawl.spiders.rsscrawl import RssCrawl
from twisted.internet import reactor
from os import listdir

class EvalCrawl(RssCrawl):
  """EvalCrawl"""

  def __init__(self, startAt):
    super(self.__class__, self).__init__(startAt)

  def handleRssEntries(self, posts):
    """TODO"""
    self.logInfo("DUDUDU" + self.allowed_domains[0])
    self.logInfo(str(

      "\n".join(filter(
        lambda _: self.allowed_domains[0] in _,
        listdir("../blogforever-crawler-publication/dataset/contents/")
      ))

      ))
    return imap(
      lambda _: Request(
        url=_.replace("{", "/"),
        meta={ "u": _.replace("{", "/") },
        dont_filter=True,
        callback=self.crawl),
      ifilter(
        lambda _: self.allowed_domains[0] in _,
        listdir("../blogforever-crawler-publication/dataset/contents/")
      ))

  def crawl(self, response):
    """TODO"""
    self.logInfo("START:" + response.meta["u"])
    parsedBody = parseHTML(response.body)
    return PostItem(url=response.meta["u"], parsedBodies=(parsedBody,))
