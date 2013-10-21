"""RssBasedCrawler"""

from bibcrawl.model.postitem import PostItem
from bibcrawl.utils.priorityheuristic import PriorityHeuristic
from bibcrawl.utils.contentextractor import ContentExtractor
from bibcrawl.utils.ohpython import *
from bibcrawl.utils.parsing import buildUrlFilter, parseHTML
from bibcrawl.utils.parsing import extractLinks, extractRssLinks
from scrapy.http import Request, Response
from scrapy.spider import BaseSpider
from twisted.internet import reactor

class RssBasedCrawler(BaseSpider):
  """I am spiderman"""
  name = "man"

  def __init__(self, domain, since=None, maxDownloads=None, *args, **kwargs):
    super(RssBasedCrawler, self).__init__(*args, **kwargs)
    self.allowed_domains = [ domain ]
    self.start_urls = [ "http://{}/".format(domain) ]
    self.maxDownloads = maxDownloads
    self.downloadsSoFar = 0
    self.seen = set()
    self.contentExtractor = None
    self.isBlogPost = None
    self.priorityHeuristic = None
    self.bufferedPosts = list()

  # except StopIteration:
  #   raise CloseSpider("No usable rss feed.")
  def parse(self, response):
    """ Step 1: Find the rss feed from the website entry point. """
    rssLinks = extractRssLinks(parseHTML(response.body), response.url)
    nextRequest = lambda: Request(
      url=rssLinks.next(),
      callback=self.parseRss,
      errback=nextRequest,
      dont_filter=True)
    return nextRequest()

  def parseRss(self, response):
    """ Step 2: Extract the desired informations on the first rss entry. """
    print response.url
    self.contentExtractor = ContentExtractor(response.body)
    for postUrl in self.contentExtractor.getRssLinks():
      yield Request(
        url=postUrl,
        callback=self.bufferPost,
        errback=self.bufferPost,
        dont_filter=True,
        # meta={ "u": _ } is here to keep a "safe" copy of the source url.
        # I don't trust response.url == (what was passed as Request url).
        meta={ "u": postUrl })

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
      foreach(lambda _: self.contentExtractor.feed(_.body, _.meta["u"]), posts)
      return iflatmap(lambda _: self.crawl(_), posts)
      # aka
      # for post in posts:
      #   self.contentExtractor.feed(post.body, post.meta["u"])
      # for post in posts:
      #   for request in self.crawl(post):
      #     yield request

  def crawl(self, response):
    """ Step 4: Recursively download all posts and extract relevant data.
    """
    parsedBody = parseHTML(response.body)
    if self.maxDownloads and self.downloadsSoFar > self.maxDownloads:
      reactor.stop()
    elif self.isBlogPost(response.url):
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
