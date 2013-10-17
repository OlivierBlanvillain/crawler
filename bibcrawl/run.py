"""main"""

# from scrapy import log
from bibcrawl.spiders import rssbasedcrawler
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
      "ITEM_PIPELINES": [
          'bibcrawl.pipelines.renderjavascript.RenderJavascript',
          'bibcrawl.pipelines.processhtml.ProcessHtml',
          'bibcrawl.pipelines.downloadimages.DownloadImages',
          'bibcrawl.pipelines.downloadfeeds.DownloadFeeds',
          'bibcrawl.pipelines.extractcomments.ExtractComments',
          'bibcrawl.pipelines.backendpropagate.BackendPropagate',
      ],
      # "HTTPCACHE_POLICY": "scrapy.contrib.httpcache.DummyPolicy",
      "HTTPCACHE_STORAGE": "scrapy.contrib.httpcache.FilesystemCacheStorage",
      "HTTPCACHE_ENABLED": True,
      "FILES_STORE": "img",

      "CONCURRENT_ITEMS": 10,
      # "CONCURRENT_REQUESTS": 1,
      # "CONCURRENT_REQUESTS_PER_DOMAIN": 1,
      # "CONCURRENT_REQUESTS_PER_IP": 1
  })

  # Need test cases for this one: letitcrash.com
  # spider = rssbasedcrawler.RssBasedCrawler(url="techcrunch.com",
  # maxDownloads=5000)
  # spider = rssbasedcrawler.RssBasedCrawler(url="keikolynn.com",
  # maxDownloads=5000)
  spider = rssbasedcrawler.RssBasedCrawler(
    url="keikolynn.com",
    maxDownloads=5000)
  crawler = Crawler(settings)

  crawler.signals.connect(reactor.stop, signals.spider_closed)
  crawler.signals.connect(reactor.getThreadPool().stop, signals.spider_closed)
  crawler.configure()
  crawler.crawl(spider)
  crawler.start()
  # log.start()
  reactor.run()

if __name__ == "__main__":
  main()
