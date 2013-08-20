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
  
  def __init__(self, blogUrl, maxPages, *args, **kwargs):
    super(RssBasedCrawler, self).__init__(*args, **kwargs)
    self.allowed_domains = [ blogUrl ]
    self.start_urls = [ "http://{}/".format(blogUrl) ]
    self.maxPages = maxPages
  
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
    self.rssTitle = entries[0].title
    self.rssAuthor = ___
    self.rssDate = ___
    self.isBlogPost = buildUrlFilter(map(lambda _: _.link, entries), True)
    return Request(entries[0].link, self.parsePost)
  
  def parsePost(self, response):
    """ Step 3: Back to the website, compute the best XPath queries to extract.
    the first rss entry.
    """
    html = etree.HTML(response.body)
    self.xPathContent = bestXPathTo(self.rssContent, html)
    self.xPathTitle = ___
    self.xPathAuthor = ___
    self.xPathDate = ___
    self.seen = set(response.url)
    print("Best XPath is: {}.".format(self.xPathContent))
    return self.fullBlog(response)
  
  def fullBlog(self, response):
    """ Step 4: Recursively download all the blog and extract relevant data.
    """
    if self.seensofar > self.maxPages:
      from twisted.internet import reactor
      reactor.stop()
    elif self.isBlogPost(response.url):
      self.seensofar += 1
      print "   " + response.url
    else:
      print "<<<" + response.url
    
    if self.isBlogPost(response.url):
      content = xPathSelectFirst(response, self.xPathContent)
      # print((content
      #       .replace(u"\n", "").replace("\t", " ").replace("  ", ""))
      #       .encode('ascii', 'replace')[:200] + " [...]")
      url = response.url
      title = ___
      author = ___
      date = ___
    
    for link in extractLinks(response):
      if link not in self.seen and link.startswith(self.start_urls[0]):
        self.seen.add(link)
        yield Request(link, self.fullBlog,
            priority=priorityHeuristic(link, response.url, self.isBlogPost))
