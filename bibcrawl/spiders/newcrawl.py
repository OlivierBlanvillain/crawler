import re
import feedparser # Doc: http://pythonhosted.org/feedparser/
from lxml import etree
from scrapy.spider import BaseSpider # Doc: https://scrapy.readthedocs.org/
from scrapy.http import Request
from utils import *
from itertools import *

___ = "TODO"

class RssBasedCrawler(BaseSpider):
  name = "man"
  seensofar = 0
  
  def __init__(self, blogUrl, *args, **kwargs):
    super(RssBasedCrawler, self).__init__(*args, **kwargs)
    self.allowed_domains = [ blogUrl ]
    self.start_urls = [ "http://{}/".format(blogUrl) ]
    
  def parse(self, response):
    """ Step 1: Find the rss feed from the website entry point.
    """
    rssLink = extractRssLink(response)
    try:
      return Request(rssLink.next(), self.parseRss)
    except StopIteration:
      raise NotImplementedError("There is no rss. TODO: fallback to page/diff?")
  
  def parseRss(self, response):
    """ Step 2: Extract the desired informations on the first rss entry.
    """
    entries = feedparser.parse(response.body).entries
    self.rssContent = entries[0].content[0].value
    self.rssTitle = ___ # entry.title
    self.rssAuthor = ___
    self.rssDate = ___
    self.postUrlFilter = buildUrlFilter(map(lambda _: _.link, entries))
    return Request(entries[0].link, self.parsePost)
  
    """ Step 3: Back to the website, compute the best XPath queries to extract.
    the first rss entry.
    """
  def parsePost(self, response):
    html = etree.HTML(response.body)
    self.xPathContent = bestXPathTo(self.rssContent, html)
    self.xPathTitle = ___
    self.xPathAuthor = ___
    self.xPathDate = ___
    self.seen = set([pruneUrl(response.url)])
    print("Best XPath is: {}.".format(self.xPathContent))
    return self.fullBlog(response)
  
  def fullBlog(self, response):
    """ Step 4: Recursively download all the blog and extract relevant data.
    """
    if self.seensofar > 10:
      from twisted.internet import reactor
      reactor.stop()
    else:
      self.seensofar += 1
    print response.url
    content = xPathSelectFirst(response, self.xPathContent)
    # print((content
    #       .replace(u"\n", "").replace("\t", " ").replace("  ", ""))
    #       .encode('ascii', 'replace')[:200] + " [...]")
    url = response.url
    title = ___
    author = ___
    date = ___
    
    prunedZipLinks = imap(lambda _: (pruneUrl(_), _), extractLinks(response))
    for (pruned, link) in prunedZipLinks:
      if pruned not in self.seen:
        self.seen.add(pruned)
        yield Request(link, self.fullBlog)
