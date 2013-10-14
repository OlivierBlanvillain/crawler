from scrapy.exceptions import DropItem

class BackendPropagate(object):
  def process_item(self, item, spider):
    try:
      print len(item.comments)
    except KeyError:
      print "No comments."
    try:
      print "comment feed!"
      print item.commentFeed
    except KeyError:
      print "No comment feed."
    return item
