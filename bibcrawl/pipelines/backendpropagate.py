from scrapy.exceptions import DropItem

class BackendPropagate(object):
  def process_item(self, item, spider):
      return item
