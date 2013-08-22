"""RssBasedCrawler """

import feedparser # http://pythonhosted.org/feedparser/
from lxml import etree # http://lxml.de/index.html#documentation
from scrapy.spider import BaseSpider # https://scrapy.readthedocs.org/
from scrapy.http import Request
from itertools import ifilter

from bibcrawl.spiders.utils import extractUrls, extractRssLink, bestXPathTo
from bibcrawl.spiders.utils import xPathSelectFirst, buildUrlFilter
from bibcrawl.spiders.scorepredictor import ScorePredictor

___ = "TODO"

class RssBasedCrawler(BaseSpider):
  """I am spiderman:"""
  name = "man"

  def __init__(self, blogUrl, maxPages, *args, **kwargs):
    super(RssBasedCrawler, self).__init__(*args, **kwargs)
    self.allowed_domains = [ blogUrl ]
    self.start_urls = [ "http://{}/".format(blogUrl) ]
    self.maxPages = maxPages
    self.seensofar = 0
    self.rssContent = ""
    self.rssTitle = ""
    self.rssAuthor = ""
    self.rssDate = ""
    self.xPathContent = ""
    self.xPathTitle = ""
    self.xPathAuthor = ""
    self.xPathDate = ""
    self.isBlogPost = ""
    self.priorityHeuristic = ""
    self.seen = set()

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
    self.priorityHeuristic = ScorePredictor()
    return Request(entries[0].link, self.parsePost)

  def parsePost(self, response):
    """ Step 3: Back to the website, compute the best XPath queries to extract.t
    the first rss entry.
    """
    html = etree.HTML(response.body)
    self.xPathContent = bestXPathTo(self.rssContent, html)
    self.xPathTitle = ___
    self.xPathAuthor = ___
    self.xPathDate = ___
    self.seen.add(response.url)
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
      print "p    " + response.url
    else:
      print "g<<<<" + response.url

    if self.isBlogPost(response.url):
      # content =
      xPathSelectFirst(response, self.xPathContent)
    #   # print((content
    #   #       .replace(u"\n", "").replace("\t", " ").replace("  ", ""))
    #   #       .encode('ascii', 'replace')[:200] + " [...]")
    #   url = ___
    #   title = ___
    #   author = ___
    #   date = ___

    urls = extractUrls(response)
    score = len(list(ifilter(self.isBlogPost, set(urls).difference(self.seen))))
    self.priorityHeuristic.feed(response.urls, score)

    for url in urls:
      if url not in self.seen and url.startswith(self.start_urls[0]):
        self.seen.add(url)
        yield Request(url, self.fullBlog, priority=self.priorityHeuristic(url))
