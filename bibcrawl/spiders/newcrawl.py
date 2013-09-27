"""RssBasedCrawler """
from bibcrawl.spiders.contentextractor import ContentExtractor
from bibcrawl.spiders.priorityheuristic import PriorityHeuristic
from bibcrawl.spiders.utils import buildUrlFilter, parseHTML
from bibcrawl.spiders.utils import extractLinks, extractRssLinks
from bibcrawl.pipelines.postitem import PostItem
from itertools import ifilter, imap, chain
from scrapy.exceptions import CloseSpider
from scrapy.http import Request, Response
from scrapy.spider import BaseSpider
from twisted.internet import reactor

class RssBasedCrawler(BaseSpider):
  """I am spiderman:"""
  name = "man"

  def __init__(self, url, maxDownloads, *args, **kwargs):
    super(RssBasedCrawler, self).__init__(*args, **kwargs)
    self.allowed_domains = [ url ]
    self.start_urls = [ "http://{}/".format(url) ]
    self.maxDownloads = maxDownloads
    self.downloadsSoFar = 0
    self.seen = set()
    self.contentExtractor = None
    self.isBlogPost = None
    self.priorityHeuristic = None
    self.bufferedPosts = list()

  def parse(self, response):
    """ Step 1: Find the rss feed from the website entry point. """
    try:
      return Request(extractRssLinks(
          response.body, response.url).next(),
          self.parseRss)
    except StopIteration:
      raise CloseSpider("There is no rss. Fallback to page/diff? TODO")

  def parseRss(self, response):
    """ Step 2: Extract the desired informations on the first rss entry. """
    print response.url
    self.contentExtractor = ContentExtractor(response.body)
    return imap(
        lambda _: Request(url=_,
            callback=self.bufferPost,
            errback=self.bufferPost,
            # meta={ "u": _ } is here to keep a "safe" copy of the source url.
            # I don't trust response.url == (what was passed as Request url).
            meta={ "u": _ }),
        self.contentExtractor.getRssLinks())

  def bufferPost(self, response):
    """ Step 3: Back to the website, compute the best XPath queries to extract
    the first rss entry.
    """
    self.bufferedPosts.append(response)
    if len(self.bufferedPosts) == len(self.contentExtractor.getRssLinks()):
      posts = tuple(ifilter(
          lambda _: isinstance(_, Response),
          self.bufferedPosts))
      self.isBlogPost = buildUrlFilter(imap(lambda _: _.url, posts))
      self.priorityHeuristic = PriorityHeuristic(self.isBlogPost)
      for post in posts:
        self.contentExtractor.feed(post.body, response.meta["u"])
      return tuple(chain.from_iterable(imap(lambda _: self.crawl(_), posts)))

  def crawl(self, response):
    """ Step 4: Recursively download all posts and extract relevant data.
    """
    parsedBody = parseHTML(response.body)
    if self.downloadsSoFar > self.maxDownloads:
      reactor.stop()
    elif self.isBlogPost(response.url):
      self.downloadsSoFar += 1
      self.contentExtractor(parsedBody)
      yield PostItem(url=response.url, parsedBody=parsedBody)

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
