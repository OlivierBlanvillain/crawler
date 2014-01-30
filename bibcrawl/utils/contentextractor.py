"""ContentExtractor"""

from bibcrawl.utils.ohpython import *
from bibcrawl.utils.parsing import parseHTML, extractFirst
from bibcrawl.utils.stringsimilarity import stringSimilarity
from bibcrawl.utils.stringsimilarity import bigrams
from feedparser import parse as feedparse

class ContentExtractor(object):
  """Extracts the content of blog posts using a RSS feed. Usage:

  >>> from urllib2 import urlopen
  >>> from bibcrawl.utils.parsing import parseHTML
  >>> pages = ("korben.info/80-bonnes-pratiques-seo.html", "korben.info/app-"
  ... "gratuite-amazon.html", "korben.info/cest-la-rentree-2.html",
  ... "korben.info/super-parkour-bros.html")
  >>> extractor = ContentExtractor(readtestdata("korben.info/feed"), printf)
  >>> extractor.feed(readtestdata(pages[0]), "http://{0}".format(pages[0]))
  >>> extractor.feed(readtestdata(pages[1]), "http://{0}".format(pages[1]))
  >>> extractor.feed(readtestdata(pages[2]), "http://{0}".format(pages[2]))
  >>> content = extractor(parseHTML(readtestdata(pages[3])))
  Best XPaths are:
  //*[@class='post-content']
  //*[@class='post-title']
  //*[@class='orange']
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
    @param parsedPage: the web page where content is extracted
    @rtype: tuple of strings
    @return: the extracted content
    """
    if self.needsRefresh:
      self._refresh()
    return tuple(imap(lambda _: extractFirst(parsedPage, _), self.xPaths))

  def _refresh(self):
    """Refreshes the XPaths with the current pages. Called internally once per
    feed+ __call__ sequence."""
    self.needsRefresh = False

    pageUrls = tuple(imap(lambda (url, _): url, self.urlZipPages))
    entries = sorted(
      ifilter(lambda _: _.link in pageUrls, self.rssEntries),
      key=lambda _: _.link)
    parsedPages = tuple(imap(
      lambda (_, page): parseHTML(page),
      sorted(
        ifilter(lambda (url, _): url in self.rssLinks, self.urlZipPages),
        key=lambda (url, _): url)))
    bestPathsPerPage = tuple(imap(
      lambda (p, e): bestPaths(p, e),
      izip(parsedPages, entries)))
    self.xPaths = tuple(imap(
      lambda _: max(set(_), key=_.count),
      izip(*bestPathsPerPage)))

    self.logger("Best XPaths are:\n" + "\n".join(self.xPaths))

def bestPaths(parsedPage, feedEntry):
  """Given a parsedPage and a feedEntry, computes the best XPath queries to
  extract relevant content from the page. The elements extracted by the
  returned queries are unknown by the caller and are hard coded in this
  method.

  @type  parsedPage: lxml.etree._Element
  @param parsedPage: target web page
  @type  feedEntry: feedparser.FeedParserDict
  @param feedEntry: web feed entry corresponding to the target page
  @return: XPath queries to extract relevant content from the page
  """
  bigramsBuffer = dict()
  queryZipExtracted = allQueries(parsedPage, bigramsBuffer)
  ssimScore = lambda target, (query, content): (
    stringSimilarity(target, content, bigramsBuffer))

  articlePath = first(max(queryZipExtracted, key=
    partial(ssimScore,feedEntry.content[0].get("value",feedEntry.description))))

  titlePath = first(max(queryZipExtracted, key=
    partial(ssimScore, feedEntry.title)))

  distancesToArticle = distancesToNode(
    articlePath, tuple(imap(first, queryZipExtracted)), parsedPage)
  dtossimScore = lambda target, (query, content): (
    stringSimilarity(target, content, bigramsBuffer)
    * 1/(distancesToArticle[query] + 1))
  authorPath = first(max(queryZipExtracted, key=
    partial(dtossimScore, feedEntry.author)))
  # datePath = first(max(queryZipExtracted, key=
  #   partial(dtossimScore, feedEntry.author)))

  # Note: Add a path to this tuple and it will be visible in the processhtml
  # pipline
  return (articlePath, titlePath, authorPath) # TBC...

def allQueries(parsedPage, bigramsBuffer):
  """Computes all the possible XPath queries. Pairs of query and extracted
  content returned.

    >>> from lxml.etree import HTML
    >>> parsedPage = HTML("<html><body><div>#1</div><div>#2<p>nested")
    >>> bigramsBuffer = dict()
    >>> allQueries(parsedPage, bigramsBuffer)
    [('/html/body/div/p', 'nested '), ('/html/body/div', '#1 '), ('/html', '#1\
 #2 nested '), ('/html/body', '#1 #2 nested ')]
    >>> bigramsBuffer
    {'#2 nested ': set(['ed', 'ne', 'd ', 'st', '2 ', '#2', 'te', 'es']), '#1\
 ': set(['1 ', '#1']), 'nested ': set(['es', 'ed', 'te', 'ne', 'd ',\
 'st']), '#1 #2 nested ': set(['ed', 'ne', 'd ', 'st', '1 ', '2 ', '#2',\
 '#1', 'te', 'es'])}

  @type  parsedPage: lxml.etree._Element
  @param parsedPage: the parsed page
  @type  bigramsBuffer: dictionary of text to set of 2-tuples for charaters
  @param bigramsBuffer: the dictionary where bigrams are pre-computed
  @rtype: pairs of string
  @return: all pairs of query, extracted content
  """
  content = dict()
  results = dict()
  # Reverse depth first preorder traversal to compute nodes texts and bigrams.
  for node in reversed(list(parsedPage.iter())):
    childrens = list(node)
    try:
      node.text = "" if not node.text else node.text + " "
    except UnicodeError:
      node.text = ""
    content[node] = node.text + "".join(imap(content.get, childrens))
    results[bestpathtonode(node)] = content[node]
    # getOrElseUpdate(results, bestpathtonode(node), lambda _: content[node])
    bigramsBuffer[content[node]] = (bigrams(node.text)
      .union(*imap(lambda _: bigramsBuffer.get(content[_], set()), childrens)))
  return list(ifilter(
    lambda _: first(_).strip() and second(_).strip(),
    results.items()))

def bestpathtonode(node):
  """Recursively computes the best path to a node.

    >>> from lxml.etree import HTML
    >>> parsedPage = HTML("<html><body><div>#1</div><div id='i'>#2<p>nested")
    >>> bestpathtonode(first(first(parsedPage)))
    '/html/body/div'
    >>> bestpathtonode(second(first(parsedPage)))
    "//*[@id='i']"
    >>> bestpathtonode(first(second(first(parsedPage))))
    "//*[@id='i']/p"

  @type  node: lxml.etree._Element
  @param node: the node
  @rtype: string
  @return: the best path
  """
  isvalid = lambda att: att and not any(imap(lambda _: _.isdigit(), att))
  return (
    "" if node is None or not isinstance(node.tag, basestring) else
    "//*[@id='{0}']".format(node.get("id")) if isvalid(node.get("id")) else
    "//*[@class='{0}']".format(node.get("class")) if isvalid(node.get("class"))
    else bestpathtonode(node.getparent()) + "/" + str(node.tag))

def distancesToNode(targetPath, queries, parsedPage):
  """Returns a map of query -> tree distance to a given target node in a page.

  >>> from lxml.etree import HTML
  >>> p = HTML("<html><body><div>#1</div><div id='i'>#2<p>nested")
  >>> distancesToNode("//*[@id='i']/p", ["/html/body", "/html/body/div"], p)
  {'/html/body': 2, '/html/body/div': 3}

  @type  targetPath: string
  @param targetPath: the target node
  @type  queries: list of strings
  @param queries: the list of queries defining the domain of the map
  @type  parsedPage: lxml.etree._Element
  @param parsedPage: the page
  @rtype: dictionary to string to integer
  @return: the distance map
  """
  parents0 = tailreq(lambda node, acc:
    acc + (node,) if(node == None)
    else tailcall(parents0)(node.getparent(), acc + (node,)) )
  parents = lambda path: parents0((parsedPage.xpath(path) + [None])[0], tuple())
  distance = lambda parents1, parents2: min(imap(
    lambda node: parents1.index(node) + parents2.index(node),
    set(parents1).intersection(set(parents2)) ))

  targetParents = parents(targetPath)
  return dict(imap(
    lambda query: (query, distance(targetParents, parents(query))),
    queries))
