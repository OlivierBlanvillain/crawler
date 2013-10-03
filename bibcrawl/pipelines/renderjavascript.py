from bibcrawl.pipelines.files import FSFilesStore
from bibcrawl.pipelines.webdriverpool import WebdriverPool
from cStringIO import StringIO
from hashlib import sha1
from scrapy.exceptions import NotConfigured
from selenium import webdriver
from selenium.common.exceptions import ElementNotVisibleException
from selenium.common.exceptions import NoSuchElementException
from twisted.internet.threads import deferToThread
from itertools import imap
from time import sleep, time

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
    defered.addErrback(lambda _: item)
    return defered

  def phantomJSProcess(self, item):
    driver = self.webdrivers.acquire()
    driver.get(item.url)
    _disqusComments(item, driver)
    _livefyreComments(item, driver)
    self.saveScreenshot(item, driver)
    self.webdrivers.release(driver)
    return item

  def saveScreenshot(self, item, driver):
    uid = sha1(item.url).hexdigest()
    png = StringIO(driver.get_screenshot_as_png())
    key = 'screen/{}.png'.format(uid)
    self.store.persist_file(key, png, None)
    item.screenshot = key

def _disqusComments(item, driver):
  iframeXPath = "//*[@id='dsq2']"
  # iframeXPath = "//iframe[@id='dsq2']"
  loadMoarXPath = "//div[@class='load-more']/a"
  commentsBody = "//div[@class='post-body']"
  try:
    frame = driver.find_element_by_xpath(iframeXPath)
    print "disqus!"
    driver.switch_to_frame(frame)
    timeout = time() + 5
    try:
      while time() < timeout:
        sleep(0.2)
        driver.find_element_by_xpath(loadMoarXPath).click()
        print "clicked"
    except ElementNotVisibleException:
      pass
    cmts = driver.find_elements_by_xpath(commentsBody)
    item.comments = tuple(imap(lambda _: _.get_attribute("innerHTML"), cmts))
    # elem.getAttribute("innerHTML");
  except NoSuchElementException:
    print "no disqus :/"
    pass
  finally:
    driver.switch_to_default_content()

def _livefyreComments(item, driver):
  # iframeXPath, loadMoarXPath = (
  #   None,
  #   "//div[@class='fyre-stream-more']"
  # )
  pass
