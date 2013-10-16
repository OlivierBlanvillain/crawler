from bibcrawl.utils.parsing import parseHTML, extractImageLinks
from bibcrawl.utils.parsing import extractRssLinks
from scrapy.exceptions import DropItem
from itertools import imap, ifilter, chain

class ProcessHtml(object):
  def process_item(self, item, spider):
    (item.content, item.title) = spider.contentExtractor(item.parsedBody)
    # More to come.
    if not (item.content):
      print "DropItem!"
      raise DropItem
    else:
      item.file_urls = extractImageLinks(item.content, item.url)
      feeds = extractRssLinks(item.parsedBody, item.url)
      item.commentFeedUrls = tuple(chain(
        (item.url + "/feed",),
        ifilter(lambda _: "comments" in _, feeds)))
      return item
