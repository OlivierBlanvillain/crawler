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
  name = "NewCrawl"
  
  def __init__(self, startAt, maxDownloads=None):
    """Instantiate a newcrawl spider for a given start url maxdownloads.
  
    @type  startat: string
    @param startat: the starting point of the crawl
    @type  maxdownloads: integer
    @param maxdownloads: the maximum number of pages to download
    """
    super(self.__class__, self).__init__(startAt)
    self.maxDownloads = maxDownloads
    self.downloadsSoFar = 0
    self.seen = set()
    self.isBlogPost = None
    self.priorityHeuristic = None

  def handleRssEntries(self, posts):
    """Handles all web-feed entries."""
    self.isBlogPost = buildUrlFilter(
      imap(lambda _: _.url, posts),
      self.logDebug)
    self.priorityHeuristic = PriorityHeuristic(self.isBlogPost)
    return iflatmap(lambda _: self.crawl(_), posts)

  def crawl(self, response):
    """Recursive crawling function emitting both PostItems in the item
    pipeline and further requests to be crawled.
    """
    parsedBody = parseHTML(response.body)
    if self.maxDownloads and self.downloadsSoFar > self.maxDownloads:
      reactor.stop()
    elif self.isBlogPost(response.url):
      # self.logInfo("> " + response.url)
      self.downloadsSoFar += 1
      yield PostItem(url=response.url, parsedBodies=(parsedBody,))

    newUrls = set(ifilter(
      lambda _: _ not in self.seen,
      extractLinks(parsedBody)))
    self.seen.update(newUrls)
    self.priorityHeuristic.feed(response.url, newUrls)
    for newUrl in newUrls:
      yield Request(
        url=newUrl,
        callback=self.crawl,
        priority=self.priorityHeuristic(newUrl))
