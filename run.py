from twisted.internet import reactor
from scrapy.crawler import Crawler
from scrapy.settings import Settings
from scrapy.xlib.pydispatch import dispatcher
from scrapy import signals
# from scrapy import log
import blogforever-crawler.spiders.newcrawl

def stop_reactor():
  reactor.stop()

if __name__=="__main__":
  dispatcher.connect(stop_reactor, signal=signals.spider_closed)
  spider = spiders.newcrawl.RssBasedCrawler("mnmlist.com")
  crawler = Crawler(Settings())
  crawler.configure()
  crawler.crawl(spider)
  crawler.start()
  # log.start()
  reactor.run()
