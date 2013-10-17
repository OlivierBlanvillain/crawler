"""RenderJavascript"""

from bibcrawl.model.commentitem import CommentItem
from bibcrawl.pipelines.files import FSFilesStore
from bibcrawl.pipelines.webdriverpool import WebdriverPool
from bibcrawl.utils.ohpython import *
from bibcrawl.utils.parsing import xPathWithClass, parseHTML, extractFirst
from collections import OrderedDict
from cStringIO import StringIO
from hashlib import sha1
from scrapy.exceptions import NotConfigured
from selenium.common.exceptions import ElementNotVisibleException
from selenium.common.exceptions import NoSuchElementException
from time import sleep, time
from twisted.internet.threads import deferToThread

class RenderJavascript(object):
  """Rendres the page with JavaScript, takes a screenshot and extract Disqus
  and Livefyre comments if present"""

  def __init__(self, storeUri):
    """Instantiate for a given storeUri. Creates"""
    if not storeUri:
      raise NotConfigured
    self.store = FSFilesStore(storeUri)
    self.webdrivers = WebdriverPool()

  @classmethod
  def from_settings(cls, settings):
    """Instantiate with storeUri from settings."""
    storeUri = settings['FILES_STORE']
    return cls(storeUri)

  def close_spider(self, _):
    """TODO"""
    self.webdrivers.stop()

  def process_item(self, item, _):
    """TODO

    @type  item: bibcrawl.model.postitem.PostItem
    @param item: the item to process
    @type  spider: scrapy.spider.BaseSpider
    @param spider: the spider that emitted this item
    @rtype: bibcrawl.model.postitem.PostItem
    @return: the processed item
    """
    # Access files downloaded by PhantomJS is WIP:
    # https://github.com/ariya/phantomjs/pull/11484
    # At some point it would be nice to get images from here instead of
    # downloading everything through Scrapy and then through PhantomJS...

    # PhantomJS asynchronous api is not yet available:
    # https://github.com/ariya/phantomjs/issues/10980#issuecomment-23601340
    # Possible workaround with twisted:
    # http://twistedmatrix.com/documents/11.0.0/core/howto/threading.html
    print("> " + item.url)

    defered = deferToThread(self.phantomJSProcess, item)
    defered.addCallback(lambda _: _)
    defered.addErrback(lambda _: item)
    return defered

  def phantomJSProcess(self, item):
    """TODO"""
    driver = self.webdrivers.acquire()
    driver.get(item.url)
    self.saveScreenshot(item, driver)
    item.comments = disqusComments(driver) + livefyreComments(driver)
    self.webdrivers.release(driver)
    return item

  def saveScreenshot(self, item, driver):
    """TODO"""
    uid = sha1(item.url).hexdigest()
    png = StringIO(driver.get_screenshot_as_png())
    key = 'screen/{}.png'.format(uid)
    self.store.persist_file(key, png, None)
    item.screenshot = key

def disqusComments(driver):
  """TODO"""
  try:
    iframe = driver.find_element_by_xpath("//*[@id='dsq2']")
  except NoSuchElementException:
    return tuple()

  driver.switch_to_frame(iframe)
  sleep(0.2)
  clickWhileVisible(driver, xPathWithClass("load-more") + "/a")
  return extractComments(
    driver=driver,
    commentXP=xPathWithClass("post"),
    contentXP="." + xPathWithClass("post-message"),
    authorXP="." + xPathWithClass("author") + "//text()",
    publishedXP="." + xPathWithClass("post-meta") + "/a/@title")
# driver.switch_to_default_content()


def clickWhileVisible(driver, xPath):
  """TODO"""
  try:
    timeout = time() + 5
    while time() < timeout:
      driver.find_element_by_xpath(xPath).click()
      sleep(0.1)
  except (ElementNotVisibleException, NoSuchElementException):
    pass

def extractComments(driver, commentXP, contentXP, authorXP, publishedXP):
  """TODO"""
  try:
    page = driver.find_element_by_xpath(".//body").get_attribute("innerHTML")
  except (ElementNotVisibleException, NoSuchElementException):
    return tuple()
  parentNodeXP = "./ancestor::" + commentXP[2:]
  getParentNode = lambda node: (node.xpath(parentNodeXP) + [None])[0]
  nodesMapComments = OrderedDict(imap(
    lambda node: (node, CommentItem(
      content=extractFirst(node, contentXP),
      author=extractFirst(node, authorXP),
      published=extractFirst(node, publishedXP),
      parent=getParentNode(node))),
    parseHTML(page).xpath(commentXP)))
  for comment in nodesMapComments.values():
    if comment.parent is not None:
      comment.parent = nodesMapComments[comment.parent]
  return tuple(ifilter(lambda _: _.content, nodesMapComments.values()))

def livefyreComments(driver):
  """TODO"""
  # try:
  #   iframe = driver.find_element_by_xpath(xPathWithClass("livefyre"))
  # except NoSuchElementException:
  #   return tuple()
  sleep(1)
  clickWhileVisible(driver, "//*[@class='fyre-stream-more-container']")
  return extractComments(
    driver=driver,
    commentXP=xPathWithClass("fyre-comment-article"),
    contentXP="." + xPathWithClass("fyre-comment"),
    authorXP="." + xPathWithClass("fyre-comment-username") + "//text()",
    publishedXP="." + xPathWithClass("fyre-comment-date") + "//text()")

# FB test case: http://www.blogger.webaholic.co.in/2011/09/facebook-comment-
# box-for-blogger.html
# JS only blog: http://nurkiewicz.blogspot.ch/
# blogspot test case w88 comments and 25 on the feed:
# http://www.keikolynn.com/2013/09/giveaway-win-chance-to-celebrate-fall.html
# Google+ comments: http://googlesystem.blogspot.ch/2013/10/the-new-google-
# gadgets.html
