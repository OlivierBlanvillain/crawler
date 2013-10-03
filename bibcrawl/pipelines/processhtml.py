from bibcrawl.spiders.parseUtils import parseHTML, extractImageLinks
from scrapy.exceptions import DropItem

class ProcessHtml(object):
  def process_item(self, item, spider):
    (item.content, item.title) = spider.contentExtractor(item.parsedBody)
    # More to come.
    if not (item.content):
      print "Dropped!"
      raise DropItem
    else:
      item.file_urls = extractImageLinks(item.content, item.url)
      return item
