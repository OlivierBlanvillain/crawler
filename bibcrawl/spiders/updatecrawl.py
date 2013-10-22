"""UpdateCrawl"""

from bibcrawl.model.postitem import PostItem
from bibcrawl.utils.contentextractor import ContentExtractor
from bibcrawl.utils.ohpython import *
from bibcrawl.utils.parsing import parseHTML, extractRssLinks
from bibcrawl.utils.parsing import datetimeFromStructtime
from scrapy.http import Request, Response
from scrapy.spider import BaseSpider

class UpdateCrawl(BaseSpider):
  """UpdateCrawl"""
  name = "UpdateCrawl"

  def __init__(self, domain, since, *args, **kwargs):
    super(UpdateCrawl, self).__init__(*args, **kwargs)
    self.allowed_domains = [ domain ]
    self.start_urls = [ "http://{}/".format(domain) ]
    self.since = since
    self.contentExtractor = None
    self.bufferedPosts = list()

  def parse(self, response):
    """."""
    rssLinks = extractRssLinks(parseHTML(response.body), response.url)
    nextRequest = lambda: Request(
      url=rssLinks.next(),
      callback=self.parseRss,
      dont_filter=True)
    return nextRequest()

  def parseRss(self, response):
    """."""
    print response.url
    self.contentExtractor = ContentExtractor(response.body)
    for postUrl in self.contentExtractor.getRssLinks():
      yield Request(
        url=postUrl,
        callback=self.bufferPost,
        errback=self.bufferPost,
        dont_filter=True,
        meta={ "u": postUrl })

  def bufferPost(self, response):
    self.bufferedPosts.append(response)
    if len(self.bufferedPosts) == len(self.contentExtractor.getRssLinks()):
      posts = tuple(ifilter(
        lambda _: isinstance(_, Response),
        self.bufferedPosts))
      foreach(lambda _: self.contentExtractor.feed(_.body, _.meta["u"]), posts)
      newRssLinks = set(imap(
        lambda _: _.link,
        ifilter(
          lambda _: datetimeFromStructtime(_.published_parsed) > self.since,
          self.contentExtractor.rssEntries)))
      return imap(
        lambda _: PostItem(url=_.url, parsedBodies=(parseHTML(_.body),)),
        ifilter(
          lambda _: _.meta["u"] in newRssLinks,
          posts))
