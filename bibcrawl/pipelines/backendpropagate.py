"""BackendPropagate"""

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
    spider.logInfo("Completed {}".format(item.url))
    # try:
    #   len(item.commentFeed)
    # except (KeyError, AttributeError):
    #   spider.logInfo("No comment feed.")
    # else:
    #   try:
    #     spider.logInfo("{} comments!".format(len(item.comments)))
    #   except (KeyError, AttributeError):
    #     spider.logInfo("No comments.")
    # return item
