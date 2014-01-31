"""Process html to extract article, title and author"""

from bibcrawl.utils.ohpython import *
from bibcrawl.utils.parsing import extractImageLinks, extractRssLinks
from scrapy.exceptions import DropItem

class ProcessHtml(object):
  """Process html page to extract content, image urls and feed urls."""

  def process_item(self, item, spider):
    """Use the spider contentExtractor to populate item.content, item.title...
    Populates image and feed urls for later download.

    @type  item: bibcrawl.model.postitem.PostItem
    @param item: the item to process
    @type  spider: scrapy.spider.BaseSpider
    @param spider: the spider that emitted this item
    @rtype: bibcrawl.model.postitem.PostItem
    @return: the processed item
    """
    extracted = spider.contentExtractor(first(item.parsedBodies))
    (item.content, item.title, item.author) = extracted # More to come.

    if not (item.content):
      spider.logInfo("Empty content: DropItem")
      raise DropItem
    else:
      item.file_urls = tuple(extractImageLinks(item.content, item.url))
      feeds = tuple(iflatmap(
        partial(extractRssLinks, url=item.url),
        item.parsedBodies))
      item.commentFeedUrls = tuple(chain(
        (item.url + "/feed",),
        ifilter(lambda _: "comments" in _, feeds)))
      return item
