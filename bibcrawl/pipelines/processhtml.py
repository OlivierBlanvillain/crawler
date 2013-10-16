from bibcrawl.utils.ohpython import *
from bibcrawl.utils.parsing import parseHTML, extractImageLinks, extractRssLinks
from scrapy.exceptions import DropItem

class ProcessHtml(object):
  def process_item(self, item, spider):
    extracted = spider.contentExtractor(first(item.parsedBodies))
    (item.content, item.title) = extracted
    # More to come.
    if not (item.content):
      print "Empty content: DropItem"
      raise DropItem
    else:
      item.file_urls = extractImageLinks(item.content, item.url)
      feeds = tuple(iflatmap(
        partial(extractRssLinks, url=item.url),
        item.parsedBodies))
      item.commentFeedUrls = tuple(chain(
        (item.url + "/feed",),
        ifilter(lambda _: "comments" in _, feeds)))
      return item
