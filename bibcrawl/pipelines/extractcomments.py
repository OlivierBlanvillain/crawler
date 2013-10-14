from bibcrawl.model.commentitem import CommentItem
from pprint import pprint
from itertools import imap, ifilter

class ProcessHtml(object):
  def process_item(self, item, spider):
    """
    if not item.feed or item.comments:
    else:

    """
    pass

  """Compute comment extraction XPaths from a list of comments and pages.

    >>> from feedparser import parse
    >>> from bibcrawl.units.mockserver import MockServer, dl
    >>> with MockServer():
    ...   pages = (dl("disqus.com/embed/comments/"), dl("korben.info/"
    ...       "hadopi-faut-il-vraiment-arreter-de-telecharger.html"))
    ...   comments = commentsFromFeed(parse(dl("disqus.com/embed/comments/")))
    ...   computeXPaths(comments, pages)
    ("//div[@class='post']", "//div[@class='post-message']", "//div[@class='author']", "//div[@class='post-meta']/a",)

  @type  comments: tuple of CommentItem
  @param comments: subset of all the comments of th page
  @type  pages: tuple of lxml.etree._Element
  @param pages: list of pages (frames of /page/n)
  @rtype: tuple of string
  @return: the computed xPaths
  """
  return ("xp", "xp", "xp", "xp")

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
      content = _.content,
      author = _.author,
      date = _.published,
      avatarUrl = None,
      parent = None),
    feed.entries))
