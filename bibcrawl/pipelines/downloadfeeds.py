"""Downloads comments web feed"""

from bibcrawl.utils.ohpython import *
from feedparser import parse as feedparse
from scrapy.contrib.pipeline.media import MediaPipeline
from scrapy.http import Request

class DownloadFeeds(MediaPipeline):
  """Downloads comments web feed"""
  def get_media_requests(self, item, _):
    return tuple(imap(
      lambda _: Request(_, dont_filter=True),
      item.commentFeedUrls))

  def item_completed(self, results, item, _):
    okResults = imap(second, ifilter(
      lambda (ok, _): ok and _.status == 200,
      results))
    try:
      item.commentFeed = feedparse(okResults.next().body)
    except StopIteration:
      pass
    return item
