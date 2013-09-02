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
  spider = newcrawl.RssBasedCrawler("huffingtonpost.com", 5000)
  crawler = Crawler(Settings({
      #RFC2616Policy,
      "HTTPCACHE_POLICY": "scrapy.contrib.httpcache.DummyPolicy",
      "HTTPCACHE_STORAGE": "scrapy.contrib.downloadermiddleware.httpcache."
          "FilesystemCacheStorage",
      "HTTPCACHE_ENABLED": True,
      # "CONCURRENT_REQUESTS": 1,
      # "CONCURRENT_REQUESTS_PER_DOMAIN": 1,
      # "CONCURRENT_REQUESTS_PER_IP": 1
  }))

  crawler.signals.connect(reactor.stop, signal=signals.spider_closed)
  crawler.configure()
  crawler.crawl(spider)
  crawler.start()
  # log.start()
  reactor.run()

if __name__ == "__main__":
  main()
