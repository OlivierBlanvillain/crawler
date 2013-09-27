from scrapy.exceptions import DropItem

class BackendPropagate(object):
  def process_item(self, item, spider):
    try:
      print item.comments
    except:
      print "No comments."
    return item
