"""ExtractComments"""

from bibcrawl.model.commentitem import CommentItem
from bibcrawl.utils.ohpython import *
from bibcrawl.utils.parsing import nodeToString, nodeQueries
from bibcrawl.utils.stringsimilarity import stringSimilarity

class ExtractComments(object):
  """Extracts comments using comment feed."""

  def process_item(self, item, spider):
    """Populates item.comments using item.commentFeed if it has not been
    already. If the feed overflows, uses some matching between the HTML tree
    and the feed comments to extract comments from the page.

    @type  item: bibcrawl.model.postitem.PostItem
    @param item: the item to process
    @type  spider: scrapy.spider.BaseSpider
    @param spider: the spider that emitted this item
    @rtype: bibcrawl.model.postitem.PostItem
    @return: the processed item
    """
    if item.commentFeed and not "comments" in item:
      comments = commentsFromFeed(item.commentFeed)
      item.comments = (
        commentsHtmlExtraction(comments, item.parsedBodies, spider.logDebug)
        if feedOverflow(item.commentFeed) else comments)
    return item


def commentsHtmlExtraction(feedComments, pages, logger):
  """Compute comment extraction XPaths from a list of comments and pages.

    >>> from feedparser import parse
    >>> from bibcrawl.utils.parsing import parseHTML
    >>> from bibcrawl.units.mockserver import MockServer, dl, printer
    >>> with MockServer():
    ...   pages = (parseHTML(dl("keikolynn.com/2013/09/giveaway-win-chance-"
    ...     "to-celebrate-fall.html")),)
    ...   comments = commentsFromFeed(parse(dl("keikolynn.com/feeds/"
    ...     "8790405898372485787/comments/default")))
    ...   cmts = commentsHtmlExtraction(comments, pages, printer)
    ("//*[@class='comment-content']", "//*[@class='user']", \
"//*[@class='datetime secondary-text']")
    >>> len(cmts)
    88

  @type  comments: tuple of CommentItem
  @param comments: subset of all the comments of th page
  @type  pages: tuple of lxml.etree._Element
  @param pages: list of pages (frames of /page/n)
  @type  logger: function of string => Unit
  @param logger: the logger
  @rtype: tuple of CommentItem
  @return: the extracted CommentItems
  """
  queries = set(iflatmap(lambda _: nodeQueries(_), pages))
  feedContents = tuple(imap(lambda _: _.content, feedComments))
  feedAuthors = tuple(imap(lambda _: _.author, feedComments))
  feedDates = tuple(imap(lambda _: _.published, feedComments))

  pathZipResults = tuple(imap(
    lambda q: (q, tuple(iflatmap(
      lambda page: imap(
        lambda _: nodeToString(_),
        page.xpath(q)),
      pages))),
    queries))

  pathZipLongResults = tuple(ifilter(
    lambda (_, result): len(result) >= len(feedComments),
    pathZipResults))

  dct = dict() # Optimisation: x14 speedup for the doctest.
  bestPR = lambda targets, candidates: max(candidates, key=
    lambda (_, result): sum(imap(
      lambda content: max(imap(
        partial(stringSimilarity, content, bufferDict=dct),
        result)),
      targets)))

  contentPathResult = bestPR(feedContents, pathZipLongResults)

  exactPR = lambda _: bestPR(_, tuple(ifilter(
    lambda (_, result): len(result) >= len(second(contentPathResult)),
    pathZipLongResults)))

  exacts = (contentPathResult, exactPR(feedAuthors), exactPR(feedDates))
  logger(tuple(imap(first, exacts)))

    # # List[String]
    # checkListOfString = lambda _: typecheck(
    #   (_, tuple), (first(_), basestring))
    # checkListOfString(feedContents)
    # checkListOfString(feedAuthors)
    # checkListOfString(feedDates)

    # # List[(String, List[String])]
    # checkListOfTupleOfStringAndListOfString = (lambda _ : typecheck(
    #   (_, tuple), (first(_), tuple), (first(first(_)), basestring),
    #   (second(first(_)), tuple), (first(second(first(_))), basestring)))
    # checkListOfTupleOfStringAndListOfString(pathZipResults)
    # checkListOfTupleOfStringAndListOfString(pathZipLongResults)
    # checkListOfTupleOfStringAndListOfString(pathZipExactResults)

  return tuple(imap(
    lambda (_1, _2, _3): CommentItem(
      content=_1, author=_2, published=_3, avatarUrl=None, parent=None),
    izip(*tuple(imap(second, exacts)))))

def feedOverflow(feed):
  """Heuristically determines they are comments on the post that are not
  showed in the feed.

    >>> from feedparser import parse
    >>> from bibcrawl.units.mockserver import MockServer, dl
    >>> with MockServer():
    ...   feedOverflow((parse(dl("korben.info/hadopi-faut-il-vraiment"
    ...     "-arreter-de-telecharger.html/feed"))))
    True

  @type  feed: feedparser.FeedParserDict
  @param feed: the feed to test
  @rtype: bool
  @return: False if there is no overflow
  """
  return len(feed.entries) >= 20

def commentsFromFeed(feed):
  """Extracts all the comments contained in a feed.

    >>> from feedparser import parse
    >>> from bibcrawl.units.mockserver import MockServer, dl
    >>> with MockServer():
    ...   comments = commentsFromFeed((parse(dl("korben.info/hadopi-faut-il"
    ...     "-vraiment-arreter-de-telecharger.html/feed"))))
    >>> len(comments)
    30

  @type  feed: feedparser.FeedParserDict
  @param feed: the feed to process
  @rtype: tuple of CommentItem
  @return: the extracted comments
  """
  return tuple(imap(
    lambda _: CommentItem(
      content=_.content[0].value,
      author=_.author,
      published=_.published,
      avatarUrl=None,
      parent=None),
    feed.entries))
