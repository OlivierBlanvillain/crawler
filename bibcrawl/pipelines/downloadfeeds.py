from bibcrawl.utils.ohpython import *
from feedparser import parse as feedparse
from scrapy.contrib.pipeline.media import MediaPipeline
from scrapy.http import Request

class DownloadFeeds(MediaPipeline):
  def get_media_requests(self, item, info):
    # dont_filter=True?
    return tuple(imap(lambda _: Request(_), item.commentFeedUrls))

  def item_completed(self, results, item, info):
    okresults = [x for ok, x in results if ok and x.status == 200]
    if len(okresults) > 0:
      item.commentFeed = feedparse(okresults[0].body)
    return item
