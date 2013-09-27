# -*- coding: utf-8 -*-

"""Utility functions for the RssBasedCrawler spider."""
import re
from itertools import imap, ifilter, chain
from unicodedata import normalize
from urlparse import urlsplit, urljoin
from lxml import etree, html
from lxml.html import soupparser

def extractLinks(page):
  """Extracts all href links of a page.

    >>> from urllib2 import urlopen
    >>> from bibcrawl.units.mockserver import MockServer, dl
    >>> with MockServer():
    ...   list(extractLinks( dl("example.com") ))
    ['http://www.iana.org/domains/example']

  @type  page: string
  @param page: the html page to process
  @rtype: collections.Iterable of strings
  @return: all the href links of the page
  """
  return ifilter(
      lambda _: _.startswith("http"),
      parseHTML(page).xpath("//a/@href"))

def extractRssLinks(page, url, parsedPage=None):
  """Extracts all the RSS and ATOM feed links of a page.

    >>> from urllib2 import urlopen
    >>> from bibcrawl.units.mockserver import MockServer
    >>> with MockServer():
    ...   list(extractRssLinks(
    ...       urlopen("http://localhost:8000/korben.info").read(),
    ...       "http://korben.info/"))[:-1]
    ['http://korben.info/feed/atom', 'http://korben.info/feed']

  @type  page: string
  @param page: the html page to process
  @type  url: string
  @param url: the page url, used to build absolute urls
  @type  parsedPage: lxml.etree._Element
  @param parsedPage: the parsed page, computed for the default value None
  @rtype: collections. Iterable of strings
  @return: all the feed links of the page
  """
  if not parsedPage:
    parsedPage = parseHTML(page)
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
  results = chain(*imap(lambda _: parsedPage.xpath(_), paths))
  return imap(lambda _: urljoin(url, _), results)


def extractImageLinks(page, url, parsedPage=None):
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
  @type  parsedPage: lxml.etree._Element
  @param parsedPage: the parsed page, computed for the default value None
  @rtype: collections. Iterable of strings
  @return: all the image links of the page
  """
  if not parsedPage:
    parsedPage = parseHTML(page)
  return imap(lambda _: urljoin(url, _), parsedPage.xpath("//img/@src"))

def buildUrlFilter(urls, debug=True):
  """Given a tuple of urls with similar pattern, computes a filtering function
  that accepts similar urls the and reject others.

    >>> times = buildUrlFilter([
    ... "http://www.thetimes.co.uk/tto/news/world/europe/article3844546.ece",
    ... "http://www.thetimes.co.uk/tto/business/industries/leisure/"
    ... "article3843571.ece" ])
    Url regex: ^http://www.thetimes.co.uk/[^/]+/[^/]+/[^/]+/[^/]+/[^/]+$
    >>> times(u"http://www.thetimes.co.uk/tto/opinion/columnists/"
    ... "philipcollins/article3844110.ece")
    True
    >>> times(u"http://www.thetimes.co.uk/tto/public/article2582551.ece")
    False

    >>> engadget = buildUrlFilter([
    ... "http://www.engadget.com/2013/08/14/back-to-school-guide-tablets/",
    ... "http://www.engadget.com/2013/08/15/we-can-do-this-hyperloop/" ])
    Url regex: ^http://www.engadget.com/\\d+/\\d+/\\d+/[^/]+/$
    >>> engadget(u"http://www.engadget.com/2013/08/15/yahoo-weather-android-"
    ... "redesign/")
    True
    >>> engadget(u"http://www.engadget.com/THATSNAN/08/15/title/")
    False

  @type  urls: collections.Iterable of strings
  @param urls: urls with a similar pattern
  @type  debug: boolean
  @param debug: enable regex print, default=False
  @rtype: function of string => boolean
  @return: the function filtering blog posts
  """
  eol = "#"
  urlsTuple = tuple(urls)
  beginsWith = lambda regex: (
      lambda str: bool(re.match(regex, str + "/" + eol)))
  (scheme, netloc, _, _, _) = urlsplit(urlsTuple[0])
  # Note that something like "[a-zA-Z]" would not be safe as it could append
  # that only one article out of many contains a digit in the title. Also if
  # we try to match more precisely the urls we might find a temporary pattern
  # like /2013/.
  patterns = ("{}://".format(scheme), netloc, eol + "$", "/", "\\d+/", "[^/]+/")
  def _bestRegex(current):
    """Recursively compute the best regex."""
    for pattern in patterns:
      if all(imap(beginsWith(current + pattern), urlsTuple)):
        return _bestRegex(current + pattern)
    return current

  if debug:
    print("Url regex: {}".format(_bestRegex("^").replace("/" + eol, "")))
  return beginsWith(_bestRegex("^"))

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
    try:
      return soupparser.fromstring(page)
    except:
      return None
