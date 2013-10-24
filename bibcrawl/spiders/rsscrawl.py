"""RssCrawl"""

from bibcrawl.utils.contentextractor import ContentExtractor
from bibcrawl.utils.ohpython import *
from bibcrawl.utils.parsing import parseHTML, extractRssLinks
from scrapy.http import Request, Response
from scrapy.spider import BaseSpider

class RssCrawl(BaseSpider):
  """RssCrawl"""
  name = "RssCrawl"

  def __init__(self, domain, *args, **kwargs):
    """TODO"""
    super(RssCrawl, self).__init__(*args, **kwargs)
    self.allowed_domains = [ domain ]
    self.start_urls = [ "http://{}/".format(domain) ]
    self.contentExtractor = None
    self.bufferedPosts = list()

  # except StopIteration:
  #   raise CloseSpider("No usable rss feed.")
  def parse(self, response):
    """TODO"""
    rssLinks = extractRssLinks(parseHTML(response.body), response.url)
    nextRequest = lambda: Request(
      url=rssLinks.next(),
      callback=self.parseRss,
      # errback=nextRequest,
      dont_filter=True)
    return nextRequest()

  def parseRss(self, response):
    """TODO"""
    print("Feed: {}".format(response.url))
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
    """TODO"""
    self.bufferedPosts.append(response)
    if len(self.bufferedPosts) == len(self.contentExtractor.getRssLinks()):
      posts = tuple(ifilter(
        lambda _: isinstance(_, Response),
        self.bufferedPosts))
      foreach(lambda _: self.contentExtractor.feed(_.body, _.meta["u"]), posts)
      return self.handleRssPosts(posts)

  def handleRssPosts(self, posts):
    """TODO"""
    pass

