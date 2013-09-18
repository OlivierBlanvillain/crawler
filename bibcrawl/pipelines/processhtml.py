from bibcrawl.spiders.utils import parseHTML, extractImageLinks
from scrapy.exceptions import DropItem

class ProcessHtml(object):
  def process_item(self, item, spider):
    (post, title) = spider.contentExtractor(item["body"])
    if not (post and title):
      print "Dropped!"
      raise DropItem
    else:
      item["file_urls"] = extractImageLinks(post, item["url"])
      return item
