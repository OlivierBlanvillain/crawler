"""Content Extractor."""
from bibcrawl.spiders.stringsimilarity import stringSimilarity
from functools import partial
from heapq import nlargest
from itertools import imap, ifilter
from lxml import etree # http://lxml.de/index.html#documentation
import feedparser # http://pythonhosted.org/feedparser/

class ContentExtractor(object):
  """Extracts the content of blog posts using a rss feed."""

  def __init__(self, rss):
    """Instantiates a content extractor for a given rss feed.

    @type  rss: scrapy.http.Response
    @param rss: the rss/atom feed
    """
    self.rssEntries = feedparser.parse(rss.body).entries
    self.rssLinks = tuple(imap(lambda _: _.link, self.rssEntries))
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
    @param url: the url of the page, as found in the rss feed
    """
    self.needsRefresh = True
    self.urlZipPages.append((url, page))

  def __call__(self, page):
    """Extracts content from a page.

    @type  page: string
    @param page: the html page to process
    @rtype: 1-tuple of strings
    @return: the extracted (content, )
    """
    if self.needsRefresh:
      self._refresh()
    parsedPage = etree.HTML(page)
    return tuple(imap(lambda _: _xPathSelectFirst(parsedPage, _), self.xPaths))

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
          key=lambda (url, _): url)))
    contents = (
        lambda _: _.content[0].value,
        # lambda _: _.title,
    )
    self.xPaths = tuple(imap(
        lambda content: _bestPath(zip(imap(content, entries), parsedPages)),
        contents))

    print("Best XPaths are: {}.".format(self.xPaths))
    from time import sleep
    sleep(100)

def _bestPath(contentZipPages):
  """Undocumented """
  nodeQueries = set(_nodeQueries(imap(lambda _: _[1], contentZipPages)))
  ratio = lambda content, page, query: (
      stringSimilarity(content, _xPathSelectFirst(page, query)))
  topQueriesForFirst = nlargest(20, nodeQueries, key=
      partial(ratio, *contentZipPages[0]))
  # sumRatio = lambda query: sum(imap(
  #   lambda (c, p): ratio(c, p, query),
  #   contentZipPages))
  topQueries = tuple(imap(
      lambda (c, p): max(topQueriesForFirst, key=partial(ratio, c, p)),
      contentZipPages))
  print "\n".join(topQueries)
  return max(set(topQueries), key=topQueries.count)
  # max(topQueriesForFirst, key=sumRatio)

def _nodeQueries(pages):
  """Compute queries to each node of the html page using per id/class global
  selection.

    >>> from lxml.etree import HTML
    >>> page = HTML("<div class='main'>#1</div><div id='footer'>#2</div> [...]")
    >>> tuple( _nodeQueries([page]) )
    ("//div[@class='main']", "//div[@id='footer']")

  @type  pages: collections.Iterable of lxml.etree._Element
  @param pages: the pages to process
  @rtype: generator of strings
  @return: the queries
  """
  for page in pages:
    for node in page.iter():
      for selector in ("id", "class"):
        for attribute in (node.get(selector) or "").split(" "):
          if attribute and not any(imap(lambda _: _.isdigit(), attribute)):
            yield "//div[@{}='{}']".format(selector, attribute)

def _xPathSelectFirst(page, query):
  """Executes a XPath query and return a string representation of the first
  result. Example:

    >>> from lxml.etree import HTML
    >>> page = HTML("<html><body><div>#1</div><div>#2<div><p>nested") # [...]
    >>> _xPathSelectFirst(page, '/html/body/div[2]/div/p')
    u'<p>nested</p>'

  @type  page: lxml.etree._Element
  @param page: the parsed page to process
  @type  query: string
  @param query: the XPath query to execute
  @rtype: string
  @return: the first result of the query, empty string if no result
  """
  # Fuck semantics. In Scala:
  # page.xpath(query).headOption.map(etree.tostring(_)).getOrElse("")
  results = page.xpath(query)
  return unicode(etree.tostring(results[0])) if(results) else u""
