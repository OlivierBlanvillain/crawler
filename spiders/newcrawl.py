import re
import feedparser
import Levenshtein

from lxml import etree
from scrapy.spider import BaseSpider
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request

# Feedparser documentation: http://pythonhosted.org/feedparser/
# Scrapy documentation: https://scrapy.readthedocs.org/
___ = "TODO"

class RssBasedCrawler(BaseSpider):
  name = "RssSpider"
  allowed_domains = ["mnmlist.com"]
  start_urls = ["http://mnmlist.com/"]
   
  seen = set()
  
  # Step 1: Find the rss feed from the website entry point.
  def parse(self, response):
    print(u"got " + response.url)
    rssUrl = extractRssLink(response)
    if rssUrl:
      return Request(rssUrl, self.parseRss)
    else:
      print("No rss :(")
  
  # Step 2: Extract the desired informations on the first rss entry.
  def parseRss(self, response):
    print(u"got " + response.url)
    entry = feedparser.parse(response.body).entries[0]
    self.rssContent = entry.content[0].value
    self.rssTitle = ___ # entry.title
    self.rssAuthor = ___
    self.rssDate = ___
    return Request(entry.link, self.parsePost)
  
  # Step 3: Back to the website, compute the best XPath queries to extract
  # the first rss entry.
  def parsePost(self, response):
    print(u"got " + response.url)
    parsed = etree.HTML(response.body)
    xPathEvaluator = lambda _: unicode(etree.tostring(parsed.xpath(_)[0]))
    tree = etree.ElementTree(parsed)
    nodePaths = map(lambda _: tree.getpath(_), parsed.iter())
    self.xPathContent = max(
        nodePaths, key=
        lambda _: Levenshtein.ratio(xPathEvaluator(_), self.rssContent))
    self.xPathTitle = ___
    self.xPathAuthor = ___
    self.xPathDate = ___
    print("Best XPath is: {}.".format(self.xPathContent))
    # return 
    self.fullBlog(response)
  
  # Step 4: Download all the blog and extract relevant data
  def fullBlog(self, response):
    print(u"\n\ngot " + response.url)
    content = xPathSelectFirst(response, self.xPathContent)
    print((content
          .replace(u"\n", "").replace("\t", " ").replace("  ", ""))
          .encode('ascii', 'replace')[:200] + " [...]")
    title = ___
    author = ___
    date = ___

    newLinks = extractHrefLinks(response, self.seen)
    self.seen = self.seen.union(newLinks)
    return map(
        lambda _: Request(_, self.fullBlog),
        newLinks)


def extractHrefLinks(response, seen):
  return filter(
      lambda _: _ not in seen,
      map(
          lambda _: _.url,
          SgmlLinkExtractor().extract_links(response)))

def extractRssLink(response):
  return xPathSelectFirst(response,
      "//link[@type='application/rss+xml'][1]/@href")

def xPathSelectFirst(response, query):
  return (
      HtmlXPathSelector(response).select(query).extract()
      or [""] # .headOption.getOrElse("") Scala, I miss you.
  )[0]
