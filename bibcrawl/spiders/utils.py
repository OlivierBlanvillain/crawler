"""Utility functions for the RssBasedCrawler spider."""
import re
from urlparse import urlsplit, urljoin
from lxml import etree
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.selector import HtmlXPathSelector
from itertools import imap, chain

def extractUrls(response):
  """Extracts all href links of a page.

  @type  response: scrapy.http.Response
  @param response: the html page to process
  @rtype: generator of strings (itertools.imap)
  @return: all the href links of the page
  """
  return imap(lambda _: _.url, SgmlLinkExtractor().extract_links(response))

def extractRssLink(response):
  """Extracts all the RSS and ATOM feed links of a page.

  @type  response: scrapy.http.Response
  @param response: the html page to process
  @rtype: generator of strings (itertools.imap)
  @return: all the feed links of the page
  """
  parser = HtmlXPathSelector(response)
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
  results = chain(*imap(lambda _: parser.select(_).extract(), paths))
  absoluts = imap(lambda _: urljoin(response.url, _), results)
  return absoluts

# def pruneUrl(url):
#   """Prunes a given url to extract only the essential information for
#   duplicate detection purpose. Note that the returned string is not a valid
#   url. Here are a few examples of pruning:

#     >>> pruneUrl("https://mnmlist.com/havent/")
#     'mnmlist.com/havent'
#     >>> pruneUrl("http://en.wikipedia.org/wiki/Pixies#Influences")
#     'en.wikipedia.org/wiki/pixies'
#     >>> pruneUrl("http://WWW.W3SCHOOLS.COM/html/html_examples.asp")
#     'www.w3schools.com/html/html_examples'

#   @type  url: string
#   @param url: the url to prune
#   @rtype: string
#   @return: the pruned url
#   """
#   (_, netloc, path, query, _) = urlsplit(url)
#   extensionRegex = ("(?i)\\.(asp|aspx|cgi|exe|fcgi|fpl|htm|html|jsp|php|"
#         + "php3|php4|php5|php6|phps|phtml|pl|py|shtm|shtml|wml)$")
#   prunedPath = re.sub(extensionRegex, "", path.rstrip("/"))
#return urlunsplit((None, netloc, prunedPath, query, None)).lstrip('/').lower()

def buildUrlFilter(urls, debug=False):
  """Given a tuple of urls with similar pattern, computes a filtering function
  that accepts similar urls the and reject others. Here are a few

    >>> times = buildUrlFilter([
    ... "http://www.thetimes.co.uk/tto/news/world/europe/article3844546.ece",
    ... "http://www.thetimes.co.uk/tto/business/industries/leisure/"
    ... "article3843571.ece" ], True)
    Url regex: ^http://www.thetimes.co.uk/[^/]+/[^/]+/[^/]+/[^/]+/[^/]+$
    >>> times(u"http://www.thetimes.co.uk/tto/opinion/columnists/"
    ... "philipcollins/article3844110.ece")
    True
    >>> times(u"http://www.thetimes.co.uk/tto/public/article2582551.ece")
    False

    >>> engadget = buildUrlFilter([
    ... "http://www.engadget.com/2013/08/14/back-to-school-guide-tablets/",
    ... "http://www.engadget.com/2013/08/15/we-can-do-this-hyperloop/" ],
    ... True)
    Url regex: ^http://www.engadget.com/\\d+/\\d+/\\d+/[^/]+/$
    >>> engadget(u"http://www.engadget.com/2013/08/15/yahoo-weather-android-"
    ... "redesign/")
    True
    >>> engadget(u"http://www.engadget.com/THATSNAN/08/15/title/")
    False

  @type  urls: tuple of strings
  @param urls: urls with a similar pattern
  @type  debug: boolean
  @param debug: enable regex print, default=False
  @rtype: function of string => boolean
  @return: the function filtering blog posts
  """
  eol = "#"
  beginsWith = lambda regex: (
      lambda str: bool(re.match(regex, str + "/" + eol)))
  (scheme, netloc, _, _, _) = urlsplit(urls[0])
  # Note that something like "[a-zA-Z]" would not be safe as it could append
  # that only one article out of many contains a digit in the title. Also if
  # we try to match more precisely the urls we might find a temporary pattern
  # like /2013/.
  patterns = ("{}://".format(scheme), netloc, eol + "$", "/", "\\d+/", "[^/]+/")
  def _bestRegex(current):
    """Recursively compute the best regex."""
    for pattern in patterns:
      if all(imap(beginsWith(current + pattern), urls)):
        return _bestRegex(current + pattern)
    return current

  if debug:
    print("Url regex: {}".format(_bestRegex("^").replace("/" + eol, "")))
  return beginsWith(_bestRegex("^"))
