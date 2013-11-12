"""RssCrawl"""

from bibcrawl.utils.contentextractor import ContentExtractor
from bibcrawl.utils.ohpython import *
from bibcrawl.utils.parsing import parseHTML, extractRssLinks
from scrapy.http import Request, Response
from scrapy.spider import BaseSpider
from scrapy import log
from urlparse import urlsplit
from scrapely import Scraper

class RssCrawl(BaseSpider):
  """Initialize a crawl with a starting page by dowloading a RSS feed and all
  its entries."""

  name = "dummy"

  def __init__(self, startAt, domain=None):
    """Instantiate for a given start url and domaine.

    @type  startAt: string
    @param startAt: the starting point of the crawl
    @type  domain: string
    @param domain: the domaine of the crawl
    """
    super(RssCrawl, self).__init__(None)
    if domain is None:
      (_, domain, _, _, _) = urlsplit(startAt)
    self.allowed_domains = (domain ,)
    self.start_urls = (startAt, )
    self.contentExtractor = None
    self.bufferedPosts = list()
    self.name = "{}@{}".format(self.__class__.__name__, domain)
    self.s = Scraper()

  def parse(self, response):
    """Extract the RSS free Request from the starting page Response.

    @type domain: scrapy.http.response.html.HtmlResponse
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

    @type response: scrapy.http.response.html.HtmlResponse
    @param response: the RSS feed
    @rtype: generator of scrapy.http.request.Request
    @return: the entry Requests
    """
    self.logInfo("Feed: {}".format(response.url))
    self.contentExtractor = ContentExtractor(response.body, self.logInfo)
    return imap(
      lambda url: Request(
        url=url,
        callback=self.bufferEntries,
        errback=self.bufferEntries,
        dont_filter=True,
        # meta={ "u": _ } is here to keep a "safe" copy of the source url.
        # I don't trust response.url == (what was passed as Request url).
        meta={ "u": url }),
      self.contentExtractor.getRssLinks())

  def bufferEntries(self, response):
    """Buffer the RSS entiry Responses, once there are all here pass the to
    the overridable handleRssEntries method.

    @type response: scrapy.http.response.html.HtmlResponse
    @param response: the RSS feed
    @rtype: generator of scrapy.http.request.Request
    @return: the entry Requests
    """
    self.bufferedPosts.append(response)
    if len(self.bufferedPosts) == len(self.contentExtractor.getRssLinks()):
      posts = tuple(ifilter(
        lambda _: isinstance(_, Response),
        self.bufferedPosts))
      foreach(lambda _: self.contentExtractor.feed(_.body, _.meta["u"]), posts)
      for post in posts:
        content = filter(
          lambda _: _.link == post.meta["u"],
          self.contentExtractor.rssEntries)[0].content[0].value
        self.s.train(post.meta["u"], {"description": content})
      return self.handleRssEntries(posts)

  def logDebug(self, string):
    """Log with spider name at debug level.

    @type  string: string
    @param string: the string to log
    """
    self.log(string, log.DEBUG)

  def logInfo(self, string):
    """Log with spider name at info level.

    @type  string: string
    @param string: the string to log
    """
    self.log(string, log.INFO)

  def logWarning(self, string):
    """Log with spider name at warning level.

    @type  string: string
    @param string: the string to log
    """
    self.log(string, log.WARNING)

  def logError(self, string):
    """Log with spider name at error level.

    @type  string: string
    @param string: the string to log
    """
    self.log(string, log.ERROR)

  def logCritical(self, string):
    """Log with spider name at critical level.

    @type  string: string
    @param string: the string to log
    """
    self.log(string, log.CRITICAL)

  def handleRssEntries(self, posts):
    """Overridable method to process all RSS entry Responses.

    @type posts: scrapy.http.posts.html.HtmlResponse
    @param posts: the RSS entries Responses
    @rtype: generator of scrapy.http.request.Request and scrapy.item.Item
    @return: the next requests and items to process
    """
    pass

