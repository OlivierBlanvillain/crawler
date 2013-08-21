from twisted.internet import reactor
from scrapy.crawler import Crawler
from scrapy.settings import Settings
from scrapy.xlib.pydispatch import dispatcher
from scrapy import signals
# from scrapy import log
import spiders.newcrawl
 
def stop_reactor():
  reactor.stop()

if __name__=="__main__":
  spider = spiders.newcrawl.RssBasedCrawler("korben.info", 500)
  crawler = Crawler(Settings())
  # crawler = Crawler(Settings({"CONCURRENT_REQUESTS": 1, "CONCURRENT_REQUESTS_PER_DOMAIN": 1, "CONCURRENT_REQUESTS_PER_IP": 1}))
  crawler.signals.connect(reactor.stop, signal=signals.spider_closed)
  crawler.configure()
  crawler.crawl(spider)
  crawler.start()
  # log.start()
  reactor.run()
