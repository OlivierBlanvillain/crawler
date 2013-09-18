"""Main entry point."""
# from scrapy import log
from bibcrawl.spiders import newcrawl
from scrapy import signals
from scrapy.crawler import Crawler
from scrapy.settings import Settings
from twisted.internet import reactor

def stop_reactor():
  """Stops the twistedreactor."""
  reactor.stop()

def main():
  """Crawler entry point."""
  settings = Settings({
      "CONCURRENT_ITEMS": 4,
      "ITEM_PIPELINES": [
          'bibcrawl.pipelines.debugprint.DebugPrint',
          'bibcrawl.pipelines.processhtml.ProcessHtml',
          'bibcrawl.pipelines.files.FilesPipeline',
          'bibcrawl.pipelines.staticcomments.StaticComments',
          'bibcrawl.pipelines.renderjavascript.RenderJavascript',
          'bibcrawl.pipelines.backendpropagate.BackendPropagate',
      ],
      "HTTPCACHE_POLICY": "scrapy.contrib.httpcache.DummyPolicy",
      "HTTPCACHE_STORAGE": "scrapy.contrib.httpcache.FilesystemCacheStorage",
      "HTTPCACHE_ENABLED": True,
      "FILES_STORE": "img"

      # "CONCURRENT_REQUESTS": 1,
      # "CONCURRENT_REQUESTS_PER_DOMAIN": 1,
      # "CONCURRENT_REQUESTS_PER_IP": 1
  })

  spider = newcrawl.RssBasedCrawler(url="korben.info", maxDownloads=500)
  crawler = Crawler(settings)

  crawler.signals.connect(reactor.stop, signal=signals.spider_closed)
  crawler.configure()
  crawler.crawl(spider)
  crawler.start()
  # log.start()
  reactor.run()

if __name__ == "__main__":
  main()
