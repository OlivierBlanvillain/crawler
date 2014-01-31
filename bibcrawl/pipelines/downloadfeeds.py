"""Downloads comments web feed"""

from bibcrawl.utils.ohpython import *
from feedparser import parse as feedparse
from scrapy.contrib.pipeline.media import MediaPipeline
from scrapy.http import Request
from scrapy import log

class DownloadFeeds(MediaPipeline):
  """Downloads comments web feed"""
  def get_media_requests(self, item, _):
    log.msg("get_media_requests", level=log.INFO)
    return Request(first(item.commentFeedUrls), dont_filter=True)
    # return tuple(imap(
    #   lambda _: Request(_, dont_filter=True),
    #   item.commentFeedUrls)) if item else tuple()

  # def media_downloaded(self, response, request, info):
  #   """Handler for success downloads"""
  #   return response

  def item_completed(self, results, item, _):
    log.msg("item_completed", level=log.INFO)
    item.commentFeed = feedparse(second(first(results)).body)
    log.msg(str(item.commentFeed), level=log.INFO)
    # okResults = imap(second, ifilter(
    #   lambda (ok, _): ok and _.status == 200,
    #   results))
    # try:
    #   item.commentFeed = feedparse(okResults.next().body)
    # except StopIteration:
    #   pass
    return item
