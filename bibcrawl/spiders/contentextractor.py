"""Content Extractor."""
from itertools import imap, ifilter
from lxml import etree # http://lxml.de/index.html#documentation
from scrapy.selector import HtmlXPathSelector
import Levenshtein
import feedparser # http://pythonhosted.org/feedparser/

class ContentExtractor(object):
  """Extracts the content of blog posts using a rss feed."""

  def __init__(self, rss):
    """Instantiates a content extractor for a given rss feed.

    @type  rss: scrapy.http.Response
    @param rss: the rss/atom feed
    """
    self.rssEntries = feedparser.parse(rss.body).entries
    self.rssLinks = tuple(imap(lambda _:_.link, self.rssEntries))
    self.urlZipPages = list()
    self.xPaths = None
    self.needsRefresh = True

  def getRssLinks(self):
    """Returns the post links extracted from the rss feed.

    @rtype: tuple of strings
    @return: the post links extracted from the rss feed
    """
    return self.rssLinks

  def feed(self, page, url):
    """Feeds the extractor with a new page.

    @type  page: string
    @param page: the html page feeded
    @type  url: string
    @param url: the url of the page, (important) as found in the rss feed
    """
    self.needsRefresh = True
    self.urlZipPages.append((url, page))

  def __call__(self, page):
    """Extracts content from a page.

    @type  page: scrapy.http.Response
    @param page: the html page to process
    @rtype: 1-tuple of strings
    @return: the extracted (content, )
    """
    if self.needsRefresh:
      self._refresh()
    return tuple(imap(lambda _: _xPathSelectFirst(page, _), self.xPaths))

  def _refresh(self):
    """Refreshes the XPaths with the current pages. Called internally once per
    (feed+, __call__) sequence."""
    self.needsRefresh = False

    # Python is so bad at this... Here is (for documentation purpose) how it
    # would be written in Scala (with url/_1 and page/_2 if urlZipPages is a
    # list of pairs and not a list of case classes):
    # val pageUrls = urlZipPages.map(_.url)
    # val entries = rssEntries.filter(pageUrls contains _.link).sortBy(_.link)
    # val parsedPages = urlZipPages.filter(rssLinks contains _.url)
    #   .sortBy(_.url).map(etree.HTML(_.page))
    pageUrls = tuple(imap(lambda (url, _): url, self.urlZipPages))
    entries = sorted(
        ifilter(lambda _: _.link in pageUrls, self.rssEntries),
        key=lambda _: _.link)
    parsedPages = tuple(imap(
        lambda (_, page): etree.HTML(page),
        sorted(
          ifilter(lambda (url, _): url in self.rssLinks, self.urlZipPages),
          ifilter(lambda (url, _): url in self.rssLinks, self.urlZipPages),
          key=lambda (url, _): url)))
    contents = (
        lambda _: _.content[0].value,
        # lambda _: _.title,
    )
    self.xPaths = tuple(imap(
        lambda _: _bestPath(zip(imap(_, entries), parsedPages)),
        contents))

    print("Best XPath is: {}.".format(self.xPaths[0]))

def _bestPath(contentZipPages):
  """lol"""
  return _bestXPathTo( * contentZipPages[0] )
  # nodePaths = imap(lambda _: etree.ElementTree(html).getpath(_), html.iter())
  # xPathEvaluator = lambda _: unicode(etree.tostring(html.xpath(_)[0]))
  # ratio = lambda _: Levenshtein.ratio(xPathEvaluator(_), string)
  # return max(nodePaths, key=ratio)

def _bestXPathTo(string, html):
  """Computes the XPath query returning the node with closest string
  representation to a given string. Here are a few examples:

    >>> page = "<html><head><title>title</title></head><body><h1>post"
    ... "</h1></body></html>"
    >>> _bestXPathTo(u"a post", etree.HTML(page))
    '/html/body/h1'
    >>> complex = "<html><body><div>#1</div><div>#2<div><p>nested"
    ... "</p></div></div></body></html>"
    >>> _bestXPathTo(u"nested", etree.HTML(complex))
    '/html/body/div[2]/div/p'

  The Levenshtein distance is used to measure string similarity. The current
  implementation iterates over all the html nodes and computes the Levenshtein
  distance to the input node for each of them. In order to improve performance
  a first filtering phase using the node length and (possibly) the character
  occurrences could be used to reduce the calls to the expensive O(n^2)
  Levenshtein algorithm.

  @type  string: string
  @param string: the string to search in the document
  @type  html: lxml.etree._Element
  @param html: the html document tree where to search for the string
  @rtype: string
  @return: the XPath query that returns the node the most similar to string
  """
  nodePaths = imap(lambda _: etree.ElementTree(html).getpath(_), html.iter())
  xPathEvaluator = lambda _: unicode(etree.tostring(html.xpath(_)[0]))
  ratio = lambda _: Levenshtein.ratio(xPathEvaluator(_), string)
  return max(nodePaths, key=ratio)

def _xPathSelectFirst(response, query):
  """Executes a XPath query and return a string representation of the first
  result. Example:

    >>> from scrapy.http import TextResponse
    >>> complex = "<html><body><div>#1</div><div>#2<div><p>nested"
    ... "</p></div></div></body></html>"
    >>> _xPathSelectFirst(TextResponse("", body=complex),
    ... '/html/body/div[2]/div/p')
    u'<p>nested</p>'

  @type  response: scrapy.http.TextResponse
  @param response: the html page to process
  @type  query: string
  @param query: the XPath query to execute
  @rtype: string
  @return: the first result of the query, empty string if no result
  """
  return (HtmlXPathSelector(response).select(query).extract()
      or [""])[0] # Fuck semantics. (in Scala: .headOption.getOrElse(""))
