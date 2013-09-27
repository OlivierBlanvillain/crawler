from bibcrawl.spiders.utils import parseHTML, extractImageLinks
from scrapy.exceptions import DropItem

class ProcessHtml(object):
  def process_item(self, item, spider):
    (item["post"], item["title"]) = spider.contentExtractor(item["parsedBody"])
    # More to come.
    if not (item["post"]):
      print "Dropped!"
      raise DropItem
    else:
      item["file_urls"] = extractImageLinks(item["post"], item["url"])
      return item
