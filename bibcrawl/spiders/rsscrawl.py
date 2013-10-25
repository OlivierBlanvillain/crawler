"""RssCrawl"""

from bibcrawl.utils.contentextractor import ContentExtractor
from bibcrawl.utils.ohpython import *
from bibcrawl.utils.parsing import parseHTML, extractRssLinks
from scrapy.http import Request, Response
from scrapy.spider import BaseSpider
from scrapy import log

class RssCrawl(BaseSpider):
  """Initialize a crawl with a starting page by dowloading a RSS feed and all
  its entries."""

  name = "dummy"

  def __init__(self, domain, *args, **kwargs):
    """Instantiate for a given domaine.

    @type  domain: string
    @param domain: the starting page
    """
    super(RssCrawl, self).__init__(*args, **kwargs)
    self.allowed_domains = [ domain ]
    self.start_urls = [ "http://{}/".format(domain) ]
    self.contentExtractor = None
    self.bufferedPosts = list()
    self.name = "{}@{}".format(self.__class__.__name__, domain)

  def parse(self, response):
    """Extract the RSS free Request from the starting page Response.

    @type: scrapy.http.response.html.HtmlResponse
    @param domain: the starting page
    @rtype: scrapy.http.request.Request
    @return: the RSS feed Request
    """
    rssLinks = extractRssLinks(parseHTML(response.body), response.url)
    nextRequest = lambda _: Request(
      url=rssLinks.next(),
      callback=self.parseRss,
      errback=nextRequest,
      dont_filter=True)
    try:
      return nextRequest(None)
    except StopIteration:
      self.logError("No usable RSS feed.")

  def parseRss(self, response):
    """Extract entry Requests from the RSS feed.

    @type: scrapy.http.response.html.HtmlResponse
    @param domain: the RSS feed
    @rtype: generator of scrapy.http.request.Request
    @return: the entry Request
    """
    self.logInfo("Feed: {}".format(response.url))
    self.contentExtractor = ContentExtractor(response.body, self.logBebug)
    return imap(
      lambda url: Request(
        url=url,
        callback=self.bufferPost,
        errback=self.bufferPost,
        dont_filter=True,
        # meta={ "u": _ } is here to keep a "safe" copy of the source url.
        # I don't trust response.url == (what was passed as Request url).
        meta={ "u": url }),
      self.contentExtractor.getRssLinks())

  def bufferPost(self, response):
    """TODO"""
    self.bufferedPosts.append(response)
    if len(self.bufferedPosts) == len(self.contentExtractor.getRssLinks()):
      posts = tuple(ifilter(
        lambda _: isinstance(_, Response),
        self.bufferedPosts))
      foreach(lambda _: self.contentExtractor.feed(_.body, _.meta["u"]), posts)
      return self.handleRssPosts(posts)

  def logDebug(self, string):
    self.log(string, log.DEBUG)

  def logInfo(self, string):
    self.log(string, log.INFO)

  def logWarning(self, string):
    self.log(string, log.WARNING)

  def logError(self, string):
    self.log(string, log.ERROR)

  def logCritical(self, string):
    self.log(string, log.CRITICAL)

  def handleRssPosts(self, posts):
    """TODO"""
    pass

