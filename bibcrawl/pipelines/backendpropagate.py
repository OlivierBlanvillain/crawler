from scrapy.exceptions import DropItem

class BackendPropagate(object):
  def process_item(self, item, spider):
    print item["comments"]
    return item
