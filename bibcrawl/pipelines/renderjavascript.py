from bibcrawl.pipelines.files import FSFilesStore
from bibcrawl.pipelines.webdriverpool import WebdriverPool
from bibcrawl.model.commentitem import CommentItem
from bibcrawl.spiders.parseUtils import xPathWithClass, parseHTML, extractFirst
from collections import OrderedDict
from cStringIO import StringIO
from hashlib import sha1
from scrapy.exceptions import NotConfigured
from selenium import webdriver
from selenium.common.exceptions import ElementNotVisibleException
from selenium.common.exceptions import NoSuchElementException
from twisted.internet.threads import deferToThread
from itertools import imap, ifilter
from time import sleep, time
from lxml import etree

class RenderJavascript(object):
  def __init__(self, store_uri):
    if not store_uri:
      raise NotConfigured
    self.store = FSFilesStore(store_uri)
    self.webdrivers = WebdriverPool()
    # self.driver = None

  @classmethod
  def from_settings(cls, settings):
    storeUri = settings['FILES_STORE']
    return cls(storeUri)

  def close_spider(self, spider):
    self.webdrivers.stop()

  def process_item(self, item, spider):
    # Access files downloaded by PhantomJS is WIP:
    # https://github.com/ariya/phantomjs/pull/11484
    # At some point it would be nice to get images from here instead of
    # downloading everything through Scrapy and then through PhantomJS...

    # PhantomJS asynchronous api is not yet available:
    # https://github.com/ariya/phantomjs/issues/10980#issuecomment-23601340
    # Possible workaround with twisted:
    # http://twistedmatrix.com/documents/11.0.0/core/howto/threading.html

    # see http://twistedmatrix.com/documents/current/core/howto/threading.html#auto2
    defered = deferToThread(self.phantomJSProcess, item)
    defered.addCallback(lambda _: _)
    # defered.addErrback(lambda _: item) TODO UǸ#
    return defered

  def phantomJSProcess(self, item):
    driver = self.webdrivers.acquire()
    driver.get(item.url)
    self.saveScreenshot(item, driver)
    item.comments = disqusComments(driver) + livefyreComments(driver)
    self.webdrivers.release(driver)
    return item

  def saveScreenshot(self, item, driver):
    uid = sha1(item.url).hexdigest()
    png = StringIO(driver.get_screenshot_as_png())
    key = 'screen/{}.png'.format(uid)
    self.store.persist_file(key, png, None)
    item.screenshot = key

def disqusComments(driver):
  try:
    iframe = driver.find_element_by_xpath("//*[@id='dsq2']")
  except NoSuchElementException:
    return tuple()

  driver.switch_to_frame(iframe)
  clickWhileVisible(driver, xPathWithClass("load-more") + "/a")
  return extractComments(
      driver=driver,
      commentXP=xPathWithClass("post"),
      contentXP="." + xPathWithClass("post-message"),
      authorXP="." + xPathWithClass("author") + "//text()",
      dateXP="." + xPathWithClass("post-meta") + "/a/@title")
  # driver.switch_to_default_content()


def clickWhileVisible(driver, xPath):
  try:
    timeout = time() + 5
    while time() < timeout:
      sleep(0.2)
      driver.find_element_by_xpath(xPath).click()
      print "clicked"
  except (ElementNotVisibleException, NoSuchElementException):
    pass

def extractComments(driver, commentXP, contentXP, authorXP, dateXP):
  page = driver.find_element_by_xpath(".//body").get_attribute("innerHTML")
  parentNodeXP = "./ancestor::" + commentXP[2:]
  getParentNode = lambda node: (node.xpath(parentNodeXP) + [None])[0]
  nodesMapComments = OrderedDict(imap(
      lambda node: (node, CommentItem(
          content=extractFirst(node, contentXP),
          author=extractFirst(node, authorXP),
          date=extractFirst(node, dateXP),
          parent=getParentNode(node))),
      parseHTML(page).xpath(commentXP)))
  for comment in nodesMapComments.values():
    if comment.parent is not None:
      comment.parent = nodesMapComments[comment.parent]
  return tuple(ifilter(lambda _: _.content, nodesMapComments.values()))

def livefyreComments(driver):
  # try:
  #   iframe = driver.find_element_by_xpath(xPathWithClass("livefyre"))
  # except NoSuchElementException:
  #   return tuple()

  clickWhileVisible(driver, xPathWithClass("fyre-stream-more"))
  return extractComments(
    driver=driver,
    commentXP=xPathWithClass("fyre-comment-article"),
    contentXP="." + xPathWithClass("fyre-comment"),
    authorXP="." + xPathWithClass("fyre-comment-username") + "//text()",
    dateXP="." + xPathWithClass("fyre-comment-date") + "//text()")

# FB test case: http://www.blogger.webaholic.co.in/2011/09/facebook-comment-box-for-blogger.html
# JS only blog: http://nurkiewicz.blogspot.ch/
# blogspot test case w88 comments and 25 on the feed: http://www.keikolynn.com/2013/09/giveaway-win-chance-to-celebrate-fall.html
