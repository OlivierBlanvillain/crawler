"""BackendPropagate"""

from scrapy.exceptions import DropItem
from scrapy import log

class BackendPropagate(object):
  """
  @type  item: bibcrawl.model.postitem.PostItem
  @param item: the item to process
  @type  spider: scrapy.spider.BaseSpider
  @param spider: the spider that emitted this item
  @rtype: bibcrawl.model.postitem.PostItem
  @return: the processed item
  """
  def process_item(self, item, spider):
    log.msg(item.url, log.INFO),
    try:
      len(item.commentFeed)
    except (KeyError, AttributeError):
      log.msg("No comment feed.", log.INFO)
    else:
      try:
        log.msg("{} comments!".format(len(item.comments)))
      except (KeyError, AttributeError):
        log.msg("No comments.", log.INFO)
    return item
