# -*- coding: utf-8 -*-

"""Utility functions for the RssBasedCrawler spider."""

from bibcrawl.utils.ohpython import *
from lxml import etree, html
from lxml.html import soupparser
from lxml.etree import SerialisationError
from re import match as rematch
from unicodedata import normalize
from urlparse import urlsplit, urljoin
from datetime import datetime
from time import mktime

def extractLinks(parsedPage):
  """Extracts all href links of a page.

    >>> from bibcrawl.utils.parsing import parseHTML
    >>> from bibcrawl.units.mockserver import MockServer, dl
    >>> with MockServer():
    ...   list(extractLinks( parseHTML(dl("example.com")) ))
    ['http://www.iana.org/domains/example']

  @type  parsedPage: lxml.etree._Element
  @param parsedPage: the html page to process
  @rtype: collections.Iterable of strings
  @return: all the href links of the page
  """
  return ifilter(
      lambda _: _.startswith("http"),
      parsedPage.xpath("//a/@href"))

def extractRssLinks(parsedPage, url):
  """Extracts all the RSS and ATOM feed links of a page.

    >>> from bibcrawl.units.mockserver import MockServer, dl
    >>> with MockServer():
    ...   list(extractRssLinks(
    ...       parseHTML(dl("korben.info")), "http://korben.info/"))[:-1]
    ['http://korben.info/feed/atom', 'http://korben.info/feed']

  @type  parsedPage: lxml.etree._Element
  @param parsedPage: the html page to process
  @type  url: string
  @param url: the page url, used to build absolute urls
  @rtype: collections. Iterable of strings
  @return: all the feed links of the page
  """
  paths = imap(lambda _: "//link[@type='{}']/@href".format(_), (
      "application/atom+xml",
      "application/atom",
      "text/atom+xml",
      "text/atom",
      "application/rss+xml",
      "application/rss",
      "text/rss+xml",
      "text/rss",
      "application/rdf+xml",
      "application/rdf",
      "text/rdf+xml",
      "text/rdf",
      "text/xml",
      "application/xml"))
  links = chain(*imap(lambda _: parsedPage.xpath(_), paths))
  fullLinks = tuple(imap(lambda _: urljoin(url, _), links))
  # Reorder the links with a simple heuristic: favor the one from on the same
  # netloc that the page.
  (_, netloc, _, _, _) = urlsplit(url)
  return chain(
    ifilter(lambda _: netloc in _, fullLinks),
    ifilter(lambda _: netloc not in _, fullLinks))


def extractImageLinks(page, url):
  """Extracts all the images links of a page.

    >>> from urllib2 import urlopen
    >>> from bibcrawl.units.mockserver import MockServer
    >>> with MockServer():
    ...   list(extractImageLinks(
    ...       urlopen("http://localhost:8000/korben.info/viber-linux.html").
    ...           read(), "http://korben.info/viber-linux.html"))[0]
    'http://korben.info/wp-content/themes/korben-steaw/hab/logo.png'

  @type  page: string
  @param page: the html page to process
  @type  url: string
  @param url: the page url, used to build absolute urls
  @rtype: collections. Iterable of strings
  @return: all the image links of the page
  """
  parsedPage = parseHTML(page)
  return imap(lambda _: urljoin(url, _), parsedPage.xpath("//img/@src"))

def extractFirst(page, query):
  """Executes a XPath query and return a string representation of the first
  result. Example:

    >>> from lxml.etree import HTML
    >>> page = HTML("<html><body><div>#1</div><div>#2<div><p>nested")
    >>> extractFirst(page, '/html/body/div[2]/div/p')
    u'<p>nested</p>'

  @type  page: lxml.etree._Element
  @param page: the parsed page to process
  @type  query: string
  @param query: the XPath query to execute
  @rtype: string
  @return: the first result of the query, empty string if no result
  """
  return nodeToString((page.xpath(query) + [""])[0])

def nodeToString(node):
  """Convert a etree node to an unicode string.

    >>> from lxml.etree import HTML
    >>> page = HTML("<html><body><div>#1</div><div>#2<p>nested")
    >>> nodeToString(page)
    u'<html><body><div>#1</div><div>#2<p>nested</p></div></body></html>'
  """
  try:
    return unicode(node if isinstance(node, (str, unicode))
      else etree.tostring(node, with_tail=False))
  except SerialisationError:
    # See this lxml bug: https://bugs.launchpad.net/lxml/+bug/400588
    return u""

def xPathFirst(path):
  """Extends a XPath query to return the first result.

    >>> xPathFirst("//*[@class='test']")
    "(//*[@class='test'])[1]"

  @type  path: string
  @param path: the initial XPath
  @rtype: string
  @return: the XPath with first result selection
  """
  return "({})[1]".format(path)

def buildUrlFilter(urls, logger=lambda _: None):
  """Given a tuple of urls with similar pattern, computes a filtering function
  that accepts similar urls the and reject others.

    >>> from bibcrawl.units.mockserver import printer
    >>> times = buildUrlFilter([
    ... "http://www.thetimes.co.uk/tto/news/world/europe/article3844546.ece",
    ... "http://www.thetimes.co.uk/tto/business/industries/leisure/"
    ... "article3843571.ece" ], printer)
    Url regex: ^http://www.thetimes.co.uk/[^/]+/[^/]+/[^/]+/[^/]+/[^/]+$
    >>> times(u"http://www.thetimes.co.uk/tto/opinion/columnists/"
    ... "philipcollins/article3844110.ece")
    True
    >>> times(u"http://www.thetimes.co.uk/tto/public/article2582551.ece")
    False

    >>> engadget = buildUrlFilter([
    ... "http://www.engadget.com/2013/08/14/back-to-school-guide-tablets/",
    ... "http://www.engadget.com/2013/08/15/we-can-do-this-hyperloop/" ]
    ... , printer)
    Url regex: ^http://www.engadget.com/\\d+/\\d+/\\d+/[^/]+/$
    >>> engadget(u"http://www.engadget.com/2013/08/15/yahoo-weather-android-"
    ... "redesign/")
    True
    >>> engadget(u"http://www.engadget.com/THATSNAN/08/15/title/")
    False

  @type  urls: collections.Iterable of strings
  @param urls: urls with a similar pattern
  @rtype: function of string => bool
  @return: the function filtering blog posts
  """
  eol = "#"
  urlsTuple = tuple(urls)
  beginsWith = lambda regex: (
      lambda str: bool(rematch(regex, str + "/" + eol)))
  (scheme, netloc, _, _, _) = urlsplit(urlsTuple[0])
  # Note that something like "[a-zA-Z]" would not be safe as it could append
  # that only one article out of many contains a digit in the title. Also if
  # we try to match more precisely the urls we might find a temporary pattern
  # like /2013/.
  patterns = ("{}://".format(scheme), netloc, eol + "$", "/", "\\d+/", "[^/]+/")
  def bestRegex(current):
    """Recursively compute the best regex."""
    for pattern in patterns:
      if all(imap(beginsWith(current + pattern), urlsTuple)):
        return bestRegex(current + pattern)
    return current

  logger("Url regex: {}".format(bestRegex("^").replace("/" + eol, "")))
  return beginsWith(bestRegex("^"))

def ascii(string):
  r"""Force convert a string to ascii.

  >>> ascii(u"École Polytechnique Fédérale de Lausanne")
  'cole Polytechnique Fdrale de Lausanne'
  >>> ascii("Et voilà.")
  'Et voil\xc3\xa0.'
  >>> ascii("problem solved")
  'problem solved'
  """
  if isinstance(string, str):
    return string
  else:
    return normalize('NFKC', string).encode('ascii','ignore')


def parseHTML(page):
  """Parses a html page with lxml. In case of errors, falls back to
  beautifulsoup.

    >>> # etree fails with an empty string:
    ... try: etree.fromstring("")
    ... except: pass
    ... else: fail
    >>> etree.tostring(parseHTML(""))
    '<html/>'

  @type  page: string
  @param page: the page to parse
  @rtype: lxml.etree._Element
  @return: the parsed page
  """
  try:
    return html.fromstring(page)
  except (etree.XMLSyntaxError, etree.ParserError):
    return soupparser.fromstring(page)

def xPathWithClass(cls):
  """Builds a XPath expression to select all elements of a page that have a
  given css class.

    >>> xPathWithClass("content")
    "//*[contains(concat(' ', normalize-space(@class), ' '), ' content ')]"

  @type  cls: string
  @param cls: the css class
  @rtype: string
  @return: the XPath expression selecting on this class
  """
  return ("//*[contains(concat(' ', normalize-space(@class), ' '), ' {} ')]"
      .format(cls))

def nodeQueries(pages):
  """Compute queries to each node of the html page using per id/class global
  selection.

    >>> from lxml.etree import HTML
    >>> page = HTML("<h1 class='title'>#1</h1><div id='footer'>#2</div> [...]")
    >>> tuple( nodeQueries([page]) )
    ("//*[@class='title']", "//*[@id='footer']")

  @type  pages: collections.Iterable of lxml.etree._Element
  @param pages: the pages to process
  @rtype: generator of strings
  @return: the queries
  """
  # selector = lambda node, sel: (lambda attribute:
  #   ("//*[@{}='{}']".format(sel, attribute), )
  #   if attribute and not any(imap(lambda _: _.isdigit(), attribute))
  #   else tuple()
  # )(node.get(sel))

  # pathSelector = lambda node: ("", )

  # return set(imap(
  #   lambda node: chain(
  #     selector(node, "id"), selector(node, "class"), pathSelector(node)
  #   ).next(),
  #   iflatmap(lambda _: _.iter(), pages)))

  for page in pages:
    for node in page.iter():
      for selector in ("id", "class"):
        attribute = node.get(selector)
        if attribute and not any(imap(lambda _: _.isdigit(), attribute)):
          yield "//*[@{}='{}']".format(selector, attribute)
          yield "//*[@{}='{}']//h1".format(selector, attribute)
          yield "//*[@{}='{}']//h2".format(selector, attribute)
          yield "//*[@{}='{}']//h3".format(selector, attribute)
          break
      else:
        pass # path
  yield "//h1"
  yield "//h2"
  yield "//h3" # TODO: clean up.


def datetimeFromStructtime(structtime):
  """Convert time.struct_time time into a datetime.

     >>> from time import localtime
     >>> type(datetimeFromStructtime(localtime()))
     <type 'datetime.datetime'>

  @type  structtime: time.struct_time
  @param structtime: the time to convert
  @rtype: datetime
  @return: the converted time
  """
  return datetime.fromtimestamp(mktime(structtime))

