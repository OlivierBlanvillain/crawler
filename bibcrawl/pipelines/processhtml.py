"""ProcessHtml"""

from bibcrawl.utils.ohpython import *
from bibcrawl.utils.parsing import extractImageLinks, extractRssLinks
from scrapy.exceptions import DropItem

from bibcrawl.utils.parsing import parseHTML
from bibcrawl.utils.stringsimilarity import cleanTags
from boilerpipe.extract import Extractor
from goose import Goose
# from readability.readability import Document
from scrapy import log
from time import time
import gc
import sys

class ProcessHtml(object):
  """Process html page to extract content, image urls and feed urls."""

  def process_item(self, item, spider):
    """Use the spider contentExtractor to populate item.content, item.title...
    Populates image and feed urls for later download.

    @type  item: bibcrawl.model.postitem.PostItem
    @param item: the item to process
    @type  spider: scrapy.spider.BaseSpider
    @param spider: the spider that emitted this item
    @rtype: bibcrawl.model.postitem.PostItem
    @return: the processed item
    """
    # def timeMeThis(e):
    #   t0 = time()
    #   e()
    #   return time() - t0
    # gcenabled = gc.isenabled()
    # gc.disable()
    # try:
    #   contentExtractor = lambda _: spider.contentExtractor(parseHTML(_))
    #   boilerpipeExtractor = lambda _: Extractor(html=_).getText()
    #   gooseExtractor = lambda _: Goose().extract(raw_html=_).cleaned_text
    #   # readabilityExtractor = lambda _: cleanTags(Document(_).summary())
    #   # CE, BP, GO, RE
    #   log.msg("{} {} {}".format(
    #     timeMeThis(partial(contentExtractor,     item.rawHtml)),
    #     timeMeThis(partial(boilerpipeExtractor,  item.rawHtml)),
    #     timeMeThis(partial(gooseExtractor,       item.rawHtml)),
    #     # timeMeThis(partial(readabilityExtractor, item.rawHtml)),
    #   ))
    # finally:
    #   if gcenabled:
    #     gc.enable()

    extracted = spider.contentExtractor(first(item.parsedBodies))
    (item.content, item.title) = extracted # More to come.

    if not (item.content):
      spider.logInfo("Empty content: DropItem")
      raise DropItem
    else:
      item.file_urls = tuple(extractImageLinks(item.content, item.url))
      feeds = tuple(iflatmap(
        partial(extractRssLinks, url=item.url),
        item.parsedBodies))
      item.commentFeedUrls = tuple(chain(
        (item.url + "/feed",),
        ifilter(lambda _: "comments" in _, feeds)))




      return item
