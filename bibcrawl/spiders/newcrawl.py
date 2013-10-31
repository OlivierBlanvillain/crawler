"""NewCrawl"""

from bibcrawl.model.postitem import PostItem
from bibcrawl.utils.priorityheuristic import PriorityHeuristic
from bibcrawl.utils.ohpython import *
from bibcrawl.utils.parsing import buildUrlFilter, parseHTML
from bibcrawl.utils.parsing import extractLinks
from scrapy.http import Request
from bibcrawl.spiders.rsscrawl import RssCrawl
from twisted.internet import reactor

class NewCrawl(RssCrawl):
  """NewCrawl"""

  def __init__(self, startAt, maxDownloads=None):
    super(self.__class__, self).__init__(startAt)
    self.maxDownloads = maxDownloads
    self.downloadsSoFar = 0
    self.seen = set()
    self.isBlogPost = None
    self.priorityHeuristic = None

  def handleRssEntries(self, posts):
    """TODO"""
    self.isBlogPost = buildUrlFilter(
      imap(lambda _: _.url, posts),
      self.logDebug)
    self.priorityHeuristic = PriorityHeuristic(self.isBlogPost)
    return iflatmap(lambda _: self.crawl(_), posts)

  def crawl(self, response):
    """TODO"""
    parsedBody = parseHTML(response.body)
    if self.maxDownloads and self.downloadsSoFar > self.maxDownloads:
      reactor.stop()
    elif self.isBlogPost(response.url):
      self.logInfo("> " + response.url)
      self.downloadsSoFar += 1
      return (PostItem(url=response.url, parsedBodies=(parsedBody,)),)

    newUrls = set(ifilter(
      lambda _: _ not in self.seen,
      extractLinks(parsedBody)))
    self.seen.update(newUrls)
    self.priorityHeuristic.feed(response.url, newUrls)
    return imap(
      lambda newUrl: Request(
        url=newUrl,
        callback=self.crawl,
        priority=self.priorityHeuristic(newUrl)),
      newUrls)
