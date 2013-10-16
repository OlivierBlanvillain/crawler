from scrapy.exceptions import DropItem

class BackendPropagate(object):
  def process_item(self, item, spider):
    print(item.url),
    try:
      len(item.commentFeed)
    except (KeyError, AttributeError):
      print "No comment feed."
    else:
      try:
        print len(item.comments), "comments!"
      except (KeyError, AttributeError):
        print "No comments."
    return item
