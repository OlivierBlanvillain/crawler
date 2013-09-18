from scrapy.exceptions import DropItem

class BackendPropagate(object):
  def process_item(self, item, spider):
    # (title, post) = spider.contentExtractor(item["body"]) # More to come.
    # if not (title and post):
    #   print "Dropped!"
    #   raise DropItem
    # else:
    #   print("\n".join(map(
    #       lambda _: ">> " + _[:200],
    #       [title, post]
    #   )))
      return item
