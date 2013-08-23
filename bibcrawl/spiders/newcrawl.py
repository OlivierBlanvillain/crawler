"""RssBasedCrawler """
from scrapy.spider import BaseSpider # https://scrapy.readthedocs.org/
from scrapy.http import Request
from itertools import ifilter, imap
from bibcrawl.spiders.utils import extractUrls, extractRssLink
from bibcrawl.spiders.utils import buildUrlFilter
from bibcrawl.spiders.scorepredictor import ScorePredictor
from bibcrawl.spiders.contentextractor import ContentExtractor

___ = "TODO"

class RssBasedCrawler(BaseSpider):
  """I am spiderman:"""
  name = "man"

  def __init__(self, blogUrl, maxDownloads, *args, **kwargs):
    """TODO"""
    super(RssBasedCrawler, self).__init__(*args, **kwargs)
    self.allowed_domains = [ blogUrl ]
    self.start_urls = [ "http://{}/".format(blogUrl) ]
    self.maxDownloads = maxDownloads
    self.downloadsSoFar = 0
    self.seen = set()
    self.contentExtractor = None
    self.isBlogPost = None
    self.priorityHeuristic = None

  def parse(self, response):
    """ Step 1: Find the rss feed from the website entry point. """
    try:
      return Request(extractRssLink(response).next(), self.parseRss)
    except StopIteration:
      raise NotImplementedError("There is no rss. Fallback to page/diff? TODO")

  def parseRss(self, response):
    """ Step 2: Extract the desired informations on the first rss entry. """
    self.contentExtractor = ContentExtractor(response)
    self.isBlogPost = buildUrlFilter(self.contentExtractor.getRssLinks(), True)
    self.priorityHeuristic = ScorePredictor(self.isBlogPost)
    return imap(
        # meta={ "u": _ } is here to keep a "safe" copy of the source url.
        # I don't trust response.url == (what was pased as Request.url).
        lambda _: Request(_, self.parsePost, meta={ "u": _ }),
        self.contentExtractor.getRssLinks())          .next()

  def parsePost(self, response):
    """ Step 3: Back to the website, compute the best XPath queries to extract
    the first rss entry.
    """
    self.contentExtractor.feed(response.body, response.meta["u"])

    self.seen.add(response.url)
    return self.fullBlog(response)

  def fullBlog(self, response):
    """ Step 4: Recursively download all the blog an-+d extract relevant data.
    """
    if self.downloadsSoFar > self.maxDownloads:
      from twisted.internet import reactor
      reactor.stop()
    elif self.isBlogPost(response.url):
      self.downloadsSoFar += 1
      print "p    " + response.url

    if self.isBlogPost(response.url):
      # content =
      self.contentExtractor(response)
    #   # print((content
    #   #       .replace(u"\n", "").replace("\t", " ").replace("  ", ""))
    #   #       .encode('ascii', 'replace')[:200] + " [...]")
    #   url = ___
    #   title = ___
    #   author = ___
    #   date = ___

    newUrls = set(ifilter(
      lambda _: _ not in self.seen and _.startswith(self.start_urls[0]), #TODO
      extractUrls(response)))
    self.seen.update(newUrls)
    self.priorityHeuristic.feed(response.url, len(newUrls))
    if not self.isBlogPost(response.url):
      print "got {} on {}".format(len(newUrls), response.url)
    return list(imap(
      lambda _: Request(_, self.fullBlog, priority=self.priorityHeuristic(_)
),
      newUrls))
