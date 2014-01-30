"""RenderJavascript"""

# Access files downloaded by PhantomJS is WIP:
# https://github.com/ariya/phantomjs/pull/11484
# At some point it would be nice to get images from here instead of
# downloading everything through Scrapy and then through PhantomJS...

# PhantomJS asynchronous api is not yet available:
# https://github.com/ariya/phantomjs/issues/10980#issuecomment-23601340

# FB test case: http://www.blogger.webaholic.co.in/2011/09/facebook-comment-
# box-for-blogger.html
# JS only blog: http://nurkiewicz.blogspot.ch/
# blogspot test case w88 comments and 25 on the feed:
# http://www.keikolynn.com/2013/09/giveaway-win-chance-to-celebrate-fall.html
# Google+ comments: http://googlesystem.blogspot.ch/2013/10/the-new-google-
# gadgets.html

from bibcrawl.model.commentitem import CommentItem
from bibcrawl.pipelines.files import FSFilesStore
from bibcrawl.pipelines.webdriverpool import WebdriverPool
from bibcrawl.utils.ohpython import *
from bibcrawl.utils.parsing import xPathWithClass, parseHTML, extractFirst
from collections import OrderedDict
from cStringIO import StringIO
from hashlib import sha1
from scrapy.contrib.closespider import CloseSpider
from selenium.common.exceptions import ElementNotVisibleException
from selenium.common.exceptions import NoSuchElementException
from time import sleep, time
from twisted.internet.threads import deferToThread

class RenderJavascript(object):
  """Rendres the page with JavaScript, takes a screenshot and extract Disqus
  and Livefyre comments if present"""

  def __init__(self, storeUri, phantomjsPath):
    """Instantiate for a given storeUri. Creates the WebriverPool.

    @type  storeUri: string
    @param storeUri: the storeUri
    @type  storeUri: string
    @param storeUri: the phantomjsPath
    """
    self.store = FSFilesStore(storeUri)
    self.webdrivers = WebdriverPool(phantomjsPath)

  @classmethod
  def from_settings(cls, settings):
    """Instantiate with storeUri from settings.

    @type  settings: scrapy.settings.Settings
    @param settings: the settings
    @rtype: RenderJavascript
    @return: the instantiated class
    """
    if not settings['FILES_STORE']:
      raise CloseSpider("FILES_STORE setting needed to save screenshots.")
    if not settings['PHANTOMJS_PATH']:
      raise CloseSpider("PHANTOMJS_PATH setting needed to save screenshots.")
    return cls(settings['FILES_STORE'], settings['PHANTOMJS_PATH'])

  def close_spider(self, _):
    """Closes the WebriverPool."""
    self.webdrivers.stop()

  def process_item(self, item, _):
    """JavaScript render item's page in a new thread. Populates
    item.screenshot and item.comments if appropriate.

    @type  item: bibcrawl.model.postitem.PostItem
    @param item: the item to process
    @type  _: scrapy.spider.BaseSpider
    @param _: the spider that emitted this item
    @rtype: bibcrawl.model.postitem.PostItem
    @return: the processed item
    """
    defered = deferToThread(self.phantomJSProcess, item)
    defered.addCallback(lambda _: _)
    defered.addErrback(lambda _: item)
    return defered

  def phantomJSProcess(self, item):
    """Acquires an idle PhantomJS driver, loads the page, saves screenshot,
    download Disqus and LiveFyre comments present and release the driver.

    @type  item: bibcrawl.model.postitem.PostItem
    @param item: the item to process
    @rtype: bibcrawl.model.postitem.PostItem
    @return: the processed item
    """
    driver = self.webdrivers.acquire()
    driver.get(item.url)
    item.comments = disqusComments(driver) # + livefyreComments(driver)
    self.saveScreenshot(item, driver)
    self.webdrivers.release(driver)
    return item

  def saveScreenshot(self, item, driver):
    """Save a screeshot of the current page in storeUri://screen/<HASH>.png.

    @type  item: bibcrawl.model.postitem.PostItem
    @param item: the item to process
    @type  driver: selenium.webdriver.phantomjs.webdriver.WebDriver
    @param driver: the driver
    """
    uid = sha1(item.url).hexdigest()
    png = StringIO(driver.get_screenshot_as_png())
    key = 'screen/{0}.png'.format(uid)
    self.store.persist_file(key, png, None)
    item.screenshot = key

def disqusComments(driver):
  """Extract comments from Disqus if present. Clicks on the "load-more" button
  while its visible to load all comments.

  @type  driver: selenium.webdriver.phantomjs.webdriver.WebDriver
  @param driver: the driver
  @rtype: tuple of CommentItem
  @return: the extracted comments
  """
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

def livefyreComments(driver):
  """Extract comments from LiveFyre if present. Clicks on the "load-more"
  button while its visible to load all comments.

  @type  driver: selenium.webdriver.phantomjs.webdriver.WebDriver
  @param driver: the driver
  @rtype: tuple of CommentItem
  @return: the extracted comments
  """
  try:
    driver.find_element_by_xpath("//*[@id='livefyre']")
  except NoSuchElementException:
    return tuple()

  sleep(2)
  clickWhileVisible(driver, "//*[@class='fyre-stream-more-container']")
  sleep(2)
  return extractComments(
    driver=driver,
    commentXP=xPathWithClass("fyre-comment-article"),
    contentXP="." + xPathWithClass("fyre-comment"),
    authorXP="." + xPathWithClass("fyre-comment-username") + "//text()",
    publishedXP="." + xPathWithClass("fyre-comment-date") + "//text()")

def clickWhileVisible(driver, xPath, maxDuration=5, stepDuration=0.5):
  """Clicks on a xPath selected element while it's visible.

  @type  driver: selenium.webdriver.phantomjs.webdriver.WebDriver
  @param driver: the driver
  @type  xPath: string
  @param xPath: the element xPath
  @type  maxDuration: int
  @param maxDuration: the maximum process duration, default = 5
  @type  stepDuration: string
  @param stepDuration: the duration between two clicks, default = 0.1
  """
  try:
    timeout = time() + maxDuration
    while time() < timeout:
      driver.find_element_by_xpath(xPath).click()
      # "document.getElementsByClassName('fyre-text')[0].click()")
      sleep(stepDuration)
  except (ElementNotVisibleException, NoSuchElementException):
    pass

def extractComments(driver, commentXP, contentXP, authorXP, publishedXP):
  """Generic procedure to extract comments from precomputed xPaths.

  @type  driver: selenium.webdriver.phantomjs.webdriver.WebDriver
  @param driver: the driver
  @type  commentXP: string
  @param commentXP: the xPath to a comment nodes
  @type  contentXP: string
  @param contentXP: the xPath to comment contents
  @type  authorXP: string
  @param authorXP: the xPath to comment authors
  @type  publishedXP: string
  @param publishedXP: the xPath to comment publication dates
  @rtype: tuple of CommentItem
  @return: the extracted comments
  """
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
  foreach(
    lambda cmmnt: cmmnt.__setattr__("parent", nodesMapComments[cmmnt.parent]),
    ifilter(lambda _: _.parent is not None, nodesMapComments.values()))
  return tuple(ifilter(lambda _: _.content, nodesMapComments.values()))
