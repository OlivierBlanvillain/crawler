from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
# from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request

class FullBlogSpider(CrawlSpider):
  name = "FullBlogSpider"
  allowed_domains = ["mnmlist.com"]
  start_urls = ["http://mnmlist.com/"]
  rules = (Rule(SgmlLinkExtractor(), callback="handlePage"), )
  
  def handlePage(self, response):
    filename = response.url.replace("/", "|")
    # open("out/" + filename, "wb").write(response.body)
    print("got " + filename)
  
  @staticmethod
  def isWordpress(body):
    return "/wp-content/" in body or "/wp-includes/" in body or "/wp-admin/" in body