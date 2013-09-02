"""Content Extractor."""
from bibcrawl.spiders.stringsimilarity import stringSimilarity
from functools import partial
from heapq import nlargest
from itertools import imap, ifilter
from lxml import etree # http://lxml.de/index.html#documentation
import feedparser # http://pythonhosted.org/feedparser/

class ContentExtractor(object):
  """Extracts the content of blog posts using a rss feed. Usage:

  >>> from urllib2 import urlopen
  >>> from bibcrawl.units.mockserver import MockServer
  >>> pages = ("korben.info/80-bonnes-pratiques-seo.html", "korben.info/app-"
  ... "gratuite-amazon.html", "korben.info/cest-la-rentree-2.html",
  ... "korben.info/super-parkour-bros.html")
  >>> with MockServer():
  ...   dl = lambda _: urlopen("http://localhost:8000/{}".format(_)).read()
  ...   extractor = ContentExtractor(dl("korben.info/feed"))
  ...   extractor.feed(dl(pages[0]), "http://{}".format(pages[0]))
  ...   extractor.feed(dl(pages[1]), "http://{}".format(pages[1]))
  ...   extractor.feed(dl(pages[2]), "http://{}".format(pages[2]))
  ...   content = extractor(dl(pages[3]))
  Best XPaths are:
  //*[@class='post-content']
  >>> len(extractor.getRssLinks())
  30
  >>> len(content[0])
  6100
  """

  def __init__(self, rss):
    """Instantiates a content extractor for a given rss feed.

    @type  rss: string
    @param rss: the rss/atom feed
    """
    self.rssEntries = feedparser.parse(rss).entries
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
        # updated, published_parsed, updated_parsed, links, title, author,
        # summary_detail, summary, content, guidislink, title_detail, href,
        # link, authors, thr_total, author_detail, id, tags, published
    )
    self.xPaths = tuple(imap(
        lambda content: _bestPath(zip(imap(content, entries), parsedPages)),
        contents))

    print("Best XPaths are:")
    print("\n".join(self.xPaths))

def _bestPath(contentZipPages):
  """Given a list of content/page, computes the best XPath query that would
  return the content on each page.

  @type  contentZipPages: list of pairs of string/lxml.etree._Element
  @param contentZipPages: the list of content/page used to guide the process
  @rtype: string
  @return: the XPath query that matches at best the content on each page
  """
  nodeQueries = set(_nodeQueries(imap(lambda _: _[1], contentZipPages)))
  ratio = lambda content, page, query: (
      stringSimilarity(content, _xPathSelectFirst(page, query)))
  topQueriesForFirst = nlargest(6, nodeQueries, key=
      partial(ratio, *contentZipPages[0]))
  topQueries = tuple(imap(
      lambda (c, p): max(topQueriesForFirst, key=partial(ratio, c, p)),
      contentZipPages))
  # DEBUG:
  from pprint import pprint
  for q in topQueriesForFirst:
    pprint(q)
    pprint(ratio(contentZipPages[0][0], contentZipPages[0][1], q))
  # from bibcrawl.spiders.stringsimilarity import _cleanTags
  # # pprint(topQueriesForFirst)
  # for q in list(topQueriesForFirst):
  #   pprint(q)
  #   pprint(_cleanTags(contentZipPages[0][0] or "dummy"))
  #   pprint(_cleanTags(_xPathSelectFirst(contentZipPages[0][1], q)))
  #   print ""

  # q = max(set(topQueries), key=topQueries.count)
  # for c, p in contentZipPages:
  #   print "..."
  #   pprint(c)
  #   pprint(_xPathSelectFirst(p, q))
  from time import sleep
  sleep(100000)
  return max(set(topQueries), key=topQueries.count)

def _nodeQueries(pages):
  """Compute queries to each node of the html page using per id/class global
  selection.

    >>> from lxml.etree import HTML
    >>> page = HTML("<h1 class='title'>#1</h1><div id='footer'>#2</div> [...]")
    >>> tuple( _nodeQueries([page]) )
    ("//*[@class='title']", "//*[@id='footer']")

  @type  pages: collections.Iterable of lxml.etree._Element
  @param pages: the pages to process
  @rtype: generator of strings
  @return: the queries
  """
  for page in pages:
    for node in page.iter():
      for selector in ("id", "class"):
        attribute = node.get(selector)
        if attribute and not any(imap(lambda _: _.isdigit(), attribute)):
          yield "//*[@{}='{}']".format(selector, attribute)

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
