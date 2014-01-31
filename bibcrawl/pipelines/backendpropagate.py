"""Saves the item in the back-end"""

from bibcrawl.utils.ohpython import *
from bibcrawl.utils.stringsimilarity import cleanTags
import feedparser
from bibcrawl.model.commentitem import CommentItem

class BackendPropagate(object):
  """Saves the item as Invenio records"""

  def process_item(self, item, spider):
    """Saves the item as Invenio records

    @type  item: bibcrawl.model.postitem.PostItem
    @param item: the item to process
    @type  spider: scrapy.spider.BaseSpider
    @param spider: the spider that emitted this item
    @rtype: bibcrawl.model.postitem.PostItem
    @return: the processed item
    """
    item.comments = commentsFromFeed(feedparser.parse(first(item.commentFeedUrls)))

    item.title = cleanTags(item.title)
    item.author = cleanTags(item.author)
    spider.logInfo((
      """Completed %(url)s %(title)s
        {0}
      """ % item).format(len(item.comments)))
# (      with file_urls %(file_urls)s
#       with files %(files)s)

    # item.files is [
    #
    # {'url': 'http://www.quantumdiaries.org/wp-
    # content/uploads/2013/04/AMS02_PositronFraction.jpg', 'path':
    # 'full/9a4c0e57d4cbbd1e4c2dc76785c735c6db9b8be3.jpg', 'checksum':
    # '3d51d326773562539825e7c5c824e551'}
    #
    # {'url': 'http://www.quantumdiaries.org/wp-content/plugins/add-to-
    # any/share_save_171_16.png', 'path':
    # 'full/2c2e7f412bc1c9a9e7c7e11980f404ba9ae4452e.png', 'checksum':
    # '6d2d5ad6a6ad4a1eac14c0179a8561aa'}]


def commentsFromFeed(feed):
  """Extracts all the comments contained in a feed.

    >>> from feedparser import parse
    >>> comments = commentsFromFeed((parse(readtestdata("korben.info/hadopi"
    ...   "-faut-il-vraiment-arreter-de-telecharger.html/feed"))))
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
      author=None,
      # author=_.author,
      published=_.published,
      avatarUrl=None,
      parent=None),
    feed.entries))
