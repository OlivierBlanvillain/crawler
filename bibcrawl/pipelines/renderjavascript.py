from bibcrawl.pipelines.files import FSFilesStore
from bibcrawl.pipelines.webdriverpool import WebdriverPool
from bibcrawl.model.commentitem import CommentItem
from bibcrawl.spiders.parseUtils import xPathWithClass, parseHTML
from bibcrawl.spiders.parseUtils import xPathFirst, extractFirst
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
    # defered.addErrback(lambda _: item)
    return defered

  def phantomJSProcess(self, item):
    driver = self.webdrivers.acquire()
    driver.get(item.url)
    item.comments = disqusComments(driver)
    # livefyreComments(driver)
    self.saveScreenshot(item, driver)
    self.webdrivers.release(driver)
    return item

  def saveScreenshot(self, item, driver):
    uid = sha1(item.url).hexdigest()
    png = StringIO(driver.get_screenshot_as_png())
    key = 'screen/{}.png'.format(uid)
    self.store.persist_file(key, png, None)
    item.screenshot = key

def disqusComments(driver):
  return tuple(extractComments(
      driver=driver,
      iframeXPath="//*[@id='dsq2']",
      showMoreXpath=xPathWithClass("load-more") + "/a",
      commentNodesXPath=xPathWithClass("post"),
      contentXPath="." + xPathWithClass("post-message"),
      authorXPath="." + xPathWithClass("author") + "//text()",
      dateXPath="." + xPathWithClass("post-meta") + "/a/@title"))

def clickWhileVisible(driver, xPath):
  try:
    timeout = time() + 5
    while time() < timeout:
      sleep(0.2)
      driver.find_element_by_xpath(xPath).click()
      print "clicked"
  except (ElementNotVisibleException, NoSuchElementException):
    pass

def extractComments(driver, iframeXPath, showMoreXpath,
  commentNodesXPath, contentXPath, authorXPath, dateXPath):
  try:
    iframe = driver.find_element_by_xpath(iframeXPath)
  except NoSuchElementException:
    return
    yield
  driver.switch_to_frame(iframe)
  clickWhileVisible(driver, showMoreXpath)
  innerPage = driver.find_element_by_xpath("//body").get_attribute("innerHTML")
  parentNodeXPath = "./ancestor::" + commentNodesXPath[2:]
  nodesMapComments = OrderedDict(imap(
      lambda node: (node, CommentItem(
          content=extractFirst(node, contentXPath),
          author=extractFirst(node, authorXPath),
          date=extractFirst(node, dateXPath),
          parent=(node.xpath(parentNodeXPath) + [None])[0])),
      parseHTML(innerPage).xpath(commentNodesXPath)))
  for comment in nodesMapComments.values():
    if comment.parent is not None:
      comment.parent = nodesMapComments[comment.parent]
    if comment.content:
      yield comment
  driver.switch_to_default_content()

def livefyreComments(driver):
  return tuple(extractComments(
    driver=driver,
    iframeXPath="//*[@id='livefyre']//iframe",
    showMoreXpath=xPathWithClass("fyre-stream-more"),
    commentNodesXPath=xPathWithClass("fyre-comment-article"),
    contentXPath="." + xPathWithClass("fyre-comment"),
    authorXPath="." + xPathWithClass("fyre-comment-username") + "//text()",
    dateXPath="." + xPathWithClass("post-meta") + "/a/@title"))
#################### not getting any comments...
#################### next is use feed on js rendred to extract the xpaths!
