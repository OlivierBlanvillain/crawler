import re
import feedparser # Doc: http://pythonhosted.org/feedparser/
from lxml import etree
from scrapy.spider import BaseSpider # Doc: https://scrapy.readthedocs.org/
from scrapy.http import Request
from utils import extractLinks, extractRssLink, xPathSelectFirst, bestXPathTo

___ = "TODO"

class RssBasedCrawler(BaseSpider):
  name = "man"
  
  seen = set()
  def __init__(self, blogUrl, *args, **kwargs):
    super(RssBasedCrawler, self).__init__(*args, **kwargs)
    self.allowed_domains = [ blogUrl ]
    self.start_urls = [ "http://{}/".format(blogUrl) ]
    
  # Step 1: Find the rss feed from the website entry point.
  def parse(self, response):
    rssLink = extractRssLink(response)
    try:
      return Request(rssLink.next(), self.parseRss)
    except StopIteration:
      raise +("There is no rss. TODO: fallback to page/diff?")
  
  # Step 2: Extract the desired informations on the first rss entry.
  def parseRss(self, response):
    entry = feedparser.parse(response.body).entries[0]
    self.rssContent = entry.content[0].value
    self.rssTitle = ___ # entry.title
    self.rssAuthor = ___
    self.rssDate = ___
    return Request(entry.link, self.parsePost)
  
  # Step 3: Back to the website, compute the best XPath queries to extract
  # the first rss entry.
  def parsePost(self, response):
    html = etree.HTML(response.body)
    self.xPathContent = bestXPathTo(self.rssContent, html)
    self.xPathTitle = ___
    self.xPathAuthor = ___
    self.xPathDate = ___
    print("Best XPath is: {}.".format(self.xPathContent))
    return self.fullBlog(response)
  
  # Step 4: Download all the blog and extract relevant data
  def fullBlog(self, response):
    content = xPathSelectFirst(response, self.xPathContent)
    print "got " + response.url
    # print((content
    #       .replace(u"\n", "").replace("\t", " ").replace("  ", ""))
    #       .encode('ascii', 'replace')[:200] + " [...]")
    url = response.url
    title = ___
    author = ___
    date = ___

    newLinks = set(extractLinks(response)).difference(self.seen)
    self.seen = self.seen.union(newLinks)
    return map(lambda _: Request(_, self.fullBlog), newLinks)
    
