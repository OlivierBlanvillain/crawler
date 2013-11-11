"""main"""

from bibcrawl.spiders.newcrawl import NewCrawl
from bibcrawl.spiders.updatecrawl import UpdateCrawl
from bibcrawl.spiders.evalcrawl import EvalCrawl
from scrapy import signals
from scrapy.crawler import Crawler
from scrapy.settings import Settings
from twisted.internet import reactor
from datetime import date, timedelta, datetime
from scrapy import log
import sys

def stop_reactor():
  """Stops the twistedreactor."""
  reactor.stop()

def startSpider(spider):
  pass

def main():
  """Crawler entry point."""
  settings = Settings({
      "ITEM_PIPELINES": [
          # 'bibcrawl.pipelines.renderjavascript.RenderJavascript',
          'bibcrawl.pipelines.processhtml.ProcessHtml',
          # 'bibcrawl.pipelines.downloadimages.DownloadImages',
          # 'bibcrawl.pipelines.downloadfeeds.DownloadFeeds',
          # 'bibcrawl.pipelines.extractcomments.ExtractComments',
          # 'bibcrawl.pipelines.backendpropagate.BackendPropagate',
          'bibcrawl.pipelines.outpropagate.OutPropagate',
      ],
      "HTTPCACHE_POLICY": "scrapy.contrib.httpcache.DummyPolicy",
      "HTTPCACHE_STORAGE": "scrapy.contrib.httpcache.FilesystemCacheStorage",
      "HTTPCACHE_ENABLED": True,
      "FILES_STORE": "img",

      # "CONCURRENT_ITEMS": 1,
      "STATS_DUMP": False,
      "LOG_LEVEL": "DEBUG",
      # "CONCURRENT_REQUESTS": 1,
      # "CONCURRENT_REQUESTS_PER_DOMAIN": 1,
      # "CONCURRENT_REQUESTS_PER_IP": 1
  })

  # Need test cases for this one: letitcrash.com
  # techcrunch.com
  # keikolynn.com

  # spider = NewCrawl(domain="korben.info", maxDownloads=500)
  # spider = UpdateCrawl(
  #   startAt="http://korben.info/feed",
  #   domain="korben.info",
  #   since=datetime.now() - timedelta(days=1))

  spider = EvalCrawl(startAt="http://" + sys.argv[1])

  crawler = Crawler(settings)

  crawler.signals.connect(reactor.stop, signals.spider_closed)
  crawler.signals.connect(reactor.getThreadPool().stop, signals.spider_closed)
  crawler.configure()
  crawler.crawl(spider)
  crawler.start()
  log.start()
  reactor.run()

if __name__ == "__main__":
  main()
