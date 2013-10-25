"""DownloadFeeds"""

from bibcrawl.utils.ohpython import *
from feedparser import parse as feedparse
from scrapy.contrib.pipeline.media import MediaPipeline
from scrapy.http import Request

class DownloadFeeds(MediaPipeline):
  """Download comments RSS feeds."""
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
    # aka
    # okresults = [x for ok, x in results if ok and x.status == 200]
    # if len(okresults) > 0:
    #   item.commentFeed = feedparse(okresults[0].body)
    # return item


