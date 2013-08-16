import re
import Levenshtein
from urlparse import urlsplit, urlunsplit, urljoin
from lxml import etree
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.selector import HtmlXPathSelector
from itertools import *


def extractLinks(response):
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


def bestXPathTo(string, html):
  """Computes the XPath query returning the node with closest string
  representation to a given string. Here are a few examples:
  
    >>> page = "<html><head><title>title</title></head><body><h1>post\\
    ... </h1></body></html>"
    >>> bestXPathTo(u"a post", etree.HTML(page))
    '/html/body/h1'
    >>> complex = "<html><body><div>#1</div><div>#2<div><p>nested\\
    ... </p></div></div></body></html>"
    >>> bestXPathTo(u"nested", etree.HTML(complex))
    '/html/body/div[2]/div/p'
  
  The U{Levenshtein<http://en.wikipedia.org/wiki/Levenshtein_distance>}
  distance is used to measure string similarity. The current implementation
  iterates over all the html nodes and computes the Levenshtein distance to
  the input node for each of them. In order to improve performance a first
  filtering phase using the node length and (possibly) the character
  occurrences could be used to reduce the calls to the expensive O(n^2)
  Levenshtein algorithm.
  
  @type  string: string
  @param string: the string to search in the document
  @type  html: lxml.etree._Element
  @param html: the html document tree where to search for the string
  @rtype: string
  @return: the XPath query that returns the node the most similar to string
  """
  # TODO fix for korben.info
  nodePaths = imap(lambda _: etree.ElementTree(html).getpath(_), html.iter())
  xPathEvaluator = lambda _: unicode(etree.tostring(html.xpath(_)[0]))
  ratio = lambda _: Levenshtein.ratio(xPathEvaluator(_), string)
  return max(nodePaths, key=ratio)


def xPathSelectFirst(response, query):
  """Executes a XPath query and return a string representation of the first
  result. Example:
  
  >>> from scrapy.http import TextResponse
  >>> complex = "<html><body><div>#1</div><div>#2<div><p>nested\\
  ... </p></div></div></body></html>"
  >>> xPathSelectFirst(TextResponse("", body=complex), '/html/body/div[2]/div/p')
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


def pruneUrl(url):
  """Prunes a given url to extract only the essential information for
  duplicate detection purpose. Note that the returned string is not a valid
  url. Here are a few examples of pruning:
  
    >>> pruneUrl("https://mnmlist.com/havent/")
    'mnmlist.com/havent'
    >>> pruneUrl("http://en.wikipedia.org/wiki/Pixies#Influences")
    'en.wikipedia.org/wiki/pixies'
    >>> pruneUrl("http://WWW.W3SCHOOLS.COM/html/html_examples.asp")
    'www.w3schools.com/html/html_examples'
  
  @type  url: string
  @param url: the url to prune
  @rtype: string
  @return: the pruned url
  """
  (scheme, netloc, path, query, fragment) = urlsplit(url)
  extensionRegex = ("(?i)\.(asp|aspx|cgi|exe|fcgi|fpl|htm|html|jsp|php|"
        + "php3|php4|php5|php6|phps|phtml|pl|py|shtm|shtml|wml)$")
  prunedPath = re.sub(extensionRegex, "", path.rstrip("/"))
  return urlunsplit((None, netloc, prunedPath, query, None)).lstrip('/').lower()


def buildUrlFilter(urls, debug=False):
  """Given a list of urls with similar pattern, computes a filtering function
  that accepts similar urls the and reject others. Here are a few
  
    >>> times = buildUrlFilter([\
        u"http://www.thetimes.co.uk/tto/news/world/europe/article3844546.ece",\
        u"http://www.thetimes.co.uk/tto/business/industries/leisure/article3843571.ece" ], True)
    DEBUG: ^http://www.thetimes.co.uk/[^/]+/[^/]+/[^/]+/[^/]+/[^/]+/
    >>> times(u"http://www.thetimes.co.uk/tto/opinion/columnists/philipcollins/article3844110.ece")
    True
    >>> times(u"http://www.thetimes.co.uk/tto/public/article2582551.ece")
    False
  
    >>> engadget = buildUrlFilter([\
        u"http://www.engadget.com/2013/08/14/back-to-school-guide-tablets/",\
        u"http://www.engadget.com/2013/08/15/we-can-do-this-hyperloop/" ], True)
    DEBUG: ^http://www.engadget.com/\d+/\d+/\d+/[^/]+//
    >>> engadget(u"http://www.engadget.com/2013/08/15/yahoo-weather-android-redesign/")
    True
    >>> engadget(u"http://www.engadget.com/THATSNAN/08/15/title/")
    False
  
  @type  urls: list of strings
  @param urls: urls with a similar pattern
  @type  debug: boolean
  @param debug: enable regex print, default=False
  @rtype: function of string => boolean
  @return: the pruned url
  """
  beginsWith = lambda regex: (
      lambda str: bool(re.match("^" + regex, str + "/")))
  (scheme, netloc, _, _, _) = urlsplit(urls[0])
  # Note that something like "[a-zA-Z]" would not be safe as it could append
  # that only one article out of many contains a digit in the title. Also if
  # we try to match more precisely the urls we might find a temporary pattern
  # like /2013/.
  patterns = (scheme, "://", netloc, "/", "\d+/", "[^/]+/")
  def _bestRegex(current):
    for pattern in patterns:
      if all(imap(beginsWith(current + pattern), urls)):
        return _bestRegex(current + pattern)
    return current
  
  if debug: print("DEBUG: {}".format(_bestRegex("^")))
  return beginsWith(_bestRegex("^"))

# Super overkill functional solution to unique url filter with project:
# links = filter(lambda _: self.allowed_domains[0] in _, extractLinks(response))
# uniquePrunedZipLinks = uniqueGroupby(links, pruneUrl)
# newPrunedZipLinks = filter(
#     lambda _: _[0] not in self.seen, 
#     uniquePrunedZipLinks)
# (newPruned, newLinks) = zip(*newPrunedZipLinks) or (list(), list())
# self.seen.update(newPruned)
# 
# See the current code for a very simple iterative alternative.
# 
# def uniqueGroupby(arg, key):
#   """Given a list(e_1, ..., e_n) and a key function, return a list of
#   (key(e_i), e_i) pairs such that the e_i are unique. Usage:
    
#     >>> uniqueGroupby("AAABBDBBDCA", lambda _: ord(_))
#     [(65, 'A'), (66, 'B'), (67, 'C'), (68, 'D')]
#     >>> # Now compare it with itertools.groupby:
#     >>> map(lambda (_1, _2): (_1, list(_2)),
#     ... groupby("AAABBDBBDCA", lambda _: ord(_)))
#     [(65, ['A', 'A', 'A']), (66, ['B', 'B']), (68, ['D']), (66, ['B', 'B']), (68, ['D']), (67, ['C']), (65, ['A'])]
  
#   @type  arg: list of T
#   @param arg: the list to uniquely group by
#   @type  key: function of T => (A <: Comparable) (implements __eq__ and __lt__)
#   @param key: the function defining equality
#   @rtype: list of (A, T) pairs
#   @return: the list of (key(e), e) pairs such that the e are unique
#   """
#   return map(
#     lambda (_1, _2): (_1, list(_2)[0]),
#     groupby(sorted(arg, key=key), key=key)
#   )
