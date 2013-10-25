
import unittest
from scrapy.exceptions import DropItem
from bibcrawl.spiders.rsscrawl import RssCrawl
from bibcrawl.pipelines.processhtml import ProcessHtml
from bibcrawl.pipelines.downloadfeeds import DownloadFeeds
from bibcrawl.utils.contentextractor import ContentExtractor
from scrapy.settings import Settings
from bibcrawl.model.postitem import PostItem
from bibcrawl.utils.parsing import parseHTML
from bibcrawl.utils.ohpython import *

class ContentExtractorTests(unittest.TestCase):
  def fromSettings(self, pipeline):
    return pipeline.fromSettings(Settings({
      "FILES_STORE": "img",
    }))

  def testProcessHtml(self):
    spider = RssCrawl("domain")
    spider.contentExtractor = lambda _: map(lambda _: "", range(2))
    processhtml = ProcessHtml()
    self.assertRaises(DropItem,
      processhtml.process_item,
      PostItem(parsedBodies=[parseHTML("test")]),
      spider)

    spider.contentExtractor = lambda _: map(str, range(2))
    url = "korben.info/viber-linux.html"
    outitem = processhtml.process_item(
      PostItem(parsedBodies=[parseHTML(url)], url=url),
      spider)

    self.assertEqual(len(outitem.file_urls), 0)
    self.assertEqual(len(outitem.commentFeedUrls), 1)

  def testDownloadFeeds(self):
    downloadfeeds = DownloadFeeds()
    requests = downloadfeeds.get_media_requests(PostItem(
      commentFeedUrls=imap(lambda _: "http://{}".format(_), range(10))
      ), None)

    self.assertEqual(len(requests), 10)
    for i in range(10):
      self.assertEqual(requests[i].url, "http://{}".format(i))

    self.assertFalse(
      "commentFeed" in downloadfeeds.item_completed(list(), PostItem(), None))


