"""ContentExtractor"""


from bibcrawl.utils.ohpython import *
from bibcrawl.utils.parsing import parseHTML, extractFirst, nodeQueries
from bibcrawl.utils.stringsimilarity import stringSimilarity, cleanTags
from feedparser import parse as feedparse
from heapq import nlargest
from scrapy.exceptions import CloseSpider
from scrapy import log
from scrapely import Scraper

class ContentExtractor(object):
  """Extracts the content of blog posts using a RSS feed. Usage:

  >>> from urllib2 import urlopen
  >>> from bibcrawl.utils.parsing import parseHTML
  >>> from bibcrawl.units.mockserver import MockServer, dl, printer
  >>> pages = ("korben.info/80-bonnes-pratiques-seo.html", "korben.info/app-"
  ... "gratuite-amazon.html", "korben.info/cest-la-rentree-2.html",
  ... "korben.info/super-parkour-bros.html")
  >>> with MockServer():
  ...   extractor = ContentExtractor(dl("korben.info/feed"), printer)
  ...   extractor.feed(dl(pages[0]), "http://{}".format(pages[0]))
  ...   extractor.feed(dl(pages[1]), "http://{}".format(pages[1]))
  ...   extractor.feed(dl(pages[2]), "http://{}".format(pages[2]))
  ...   content = extractor(parseHTML(dl(pages[3])))
  Best XPaths are:
  //*[@class='post-content']
  //*[@class='post-title']
  >>> len(extractor.getRssLinks())
  30
  >>> 6000 < len(content[0]) < 6200
  True
  """

  def __init__(self, rss, logger=lambda _: None):
    """Instantiates a content extractor for a given RSS feed.

    @type  rss: string
    @param rss: the rss/atom feed
    @type  logger: function of string => Unit
    @param logger: the logger
    """
    self.rssEntries = feedparse(rss).entries
    self.rssLinks = tuple(imap(lambda _: _.link, self.rssEntries))
    self.logger = logger
    self.urlZipPages = list()
    self.xPaths = None
    self.needsRefresh = True
    self.s = Scraper()

  def getRssLinks(self):
    """Returns the post links extracted from the RSS feed.

    @rtype: tuple of strings
    @return: the post links extracted from the RSS feed
    """
    return self.rssLinks

  def feed(self, page, url):
    """Feeds the extractor with a new page. Careful, the urls feeded here must
    match one url found in the RSS feed provided in the constructor.

    @type  page: string
    @param page: the html page feeded
    @type  url: string
    @param url: the url of the page, as found in the RSS feed
    """
    self.needsRefresh = True
    self.urlZipPages.append((url, page))

  def __call__(self, parsedPage):
    """Extracts content from a page.

    @type  parsedPage: lxml.etree._Element
    @param parsedPage: the parsed page, computed for the default value None
    @rtype: 1-tuple of strings
    @return: the extracted (content, )
    """
    if self.needsRefresh:
      self._refresh()
# return tuple(imap(lambda _: extractFirst(parsedPage, _), self.xPaths))
    return self.s.scrape_page(parsedPage)

  def _refresh(self):
    """Refreshes the XPaths with the current pages. Called internally once per
    feed+ __call__ sequence."""
    self.needsRefresh = False


    # Python is so bad at this... Here is (for documentation purpose) how it
    # would be written in Scala (with url/_1 and page/_2 if urlZipPages is a
    # list of pairs and not a list of case classes):
    # val pageUrls = urlZipPages.map(_.url)
    # val entries = rssEntries.filter(pageUrls contains _.link).sortBy(_.link)
    # val parsedPages = urlZipPages.filter(rssLinks contains _.url)
    #   .sortBy(_.url).map(parseHTML(_.page))
    pageUrls = tuple(imap(lambda (url, _): url, self.urlZipPages))
    entries = sorted(
      ifilter(lambda _: _.link in pageUrls, self.rssEntries),
      key=lambda _: _.link)
    parsedPages = tuple(imap(
      lambda (_, page): parseHTML(page),
      sorted(
        ifilter(lambda (url, _): url in self.rssLinks, self.urlZipPages),
        key=lambda (url, _): url)))
    extractors = (
      extractContent,
      # lambda _: _.title,
      # updated, published_parsed, updated_parsed, links, title, author,
      # summary_detail, summary, content, guidislink, title_detail, href,
      # link, authors, thr_total, author_detail, id, tags, published
    )

# self.xPaths = tuple(imap(
#   lambda extractr: bestPath(tuple(izip(
#     imap(extractr, entries),
#     parsedPages))),
#   extractors))

# self.logger("Best XPaths are:\n" + "\n".join(self.xPaths))
    from scrapely.htmlpage import HtmlPage
    urls = tuple(imap(
      lambda (_, page): _,
      sorted(
        ifilter(lambda (url, _): url in self.rssLinks, self.urlZipPages),
        key=lambda (url, _): url)))
    for (content, url) in izip(imap(extractContent, entries), urls):
      if page is not None:
        self.s.train(url), { "description": content })

def extractContent(feed):
  """Returns feed content value, or description if apsent."""
  try:
    return feed.content[0].value
  except AttributeError:
    try:
      return feed.description
    except AttributeError:
      raise CloseSpider("Feed entry has no content and no description")

def bestPath(contentZipPages):
  """Given a list of content/page, computes the best XPath query that would
  return the content on each page.

  @type  contentZipPages: list of pairs of string/lxml.etree._Element
  @param contentZipPages: the list of content/page used to guide the process
  @rtype: string
  @return: the XPath query that matches at best the content on each page
  """
  nonEmptyContentZipPages = contentZipPages
  # nonEmptyContentZipPages = tuple(ifilter(
  #   lambda (content, _): cleanTags(content),
  #   contentZipPages))
  queries = set(nodeQueries(imap(lambda _: _[1], nonEmptyContentZipPages)))
  dct = dict()
  ratio = lambda content, page, query: (
    stringSimilarity(content, extractFirst(page, query), dct))
  topQueries = tuple(imap(
    lambda (c, p): max(queries, key=partial(ratio, c, p)),
    nonEmptyContentZipPages))
  return max(set(topQueries), key=topQueries.count)

  # topQueriesForFirst = nlargest(6, queries, key=
  #   partial(ratio, *contentZipPages[0]))
  # topQueries = tuple(imap(
  #   lambda (c, p): max(topQueriesForFirst, key=partial(ratio, c, p)),
  #   contentZipPages))

  # return max(set(topQueries), key=topQueries.count)
