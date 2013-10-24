"""BackendPropagate"""

from scrapy.exceptions import DropItem

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
    print(item.url),
    try:
      len(item.commentFeed)
    except (KeyError, AttributeError):
      print("No comment feed.")
    else:
      try:
        print("{} comments!".format(len(item.comments)))
      except (KeyError, AttributeError):
        print("No comments.")
    return item
