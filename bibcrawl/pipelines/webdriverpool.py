from Queue import Queue, Empty
from selenium import webdriver
from itertools import imap

class WebdriverPool(object):
  def __init__(self):
    self.all = Queue()
    self.available = Queue()
    self.stopped = False

  def acquire(self):
    if not self.stopped:
      try:
        return self.available.get_nowait()
      except Empty:
        return self._createWebdriver()

  def _createWebdriver(self):
    # TODO try: except selenium.common.exceptions.WebDriverException:
    driver = webdriver.PhantomJS("./lib/phantomjs/bin/phantomjs")
    self.all.put_nowait(driver)
    return driver

  def release(self, driver):
    self.available.put_nowait(driver)

  def stop(self):
    self.stopped = True
    if not self.all.empty():
      for driver in self.all:
        driver.quit()
