"""WebdriverPool"""

from bibcrawl.utils.ohpython import *
from Queue import Queue, Empty
from selenium import webdriver

class WebdriverPool(object):
  """Manages a thread safe pool of PhantomJS processes.

    >>> wd = WebdriverPool()
    >>> driver = wd.acquire()
    >>> driver.get("www.google.com") # use driver...
    >>> wd.release(driver)
    >>> wd.stop()
    >>> wd.acquire() is None
    True
  """
  def __init__(self):
    """Creates a new WebdriverPool instance with two empty queues."""
    self.all = Queue()
    self.available = Queue()
    self.stopped = False

  def acquire(self):
    """Acquires a webdriver, if the available queue is empty a new process is
    created. When called after stop this method return None.

    @rtype: selenium.webdriver.phantomjs.webdriver.WebDriver
    @return: an PhantomJS webdriver
    """
    if not self.stopped:
      try:
        return self.available.get_nowait()
      except Empty:
        driver = webdriver.PhantomJS("./lib/phantomjs/bin/phantomjs")
        self.all.put(driver)
        return driver

  def release(self, driver):
    """Releases a webdriver, the freed resource will be reused on the next
    acquire call.

    @type  driver: selenium.webdriver.phantomjs.webdriver.WebDriver
    @param driver: the released driver
    """
    self.available.put(driver)

  def stop(self):
    """Stops the webdriver pool, quits all started processes and prevent
    creation of further processes."""
    self.stopped = True
    while True:
      try:
        driver = self.all.get(block=False)
        driver.quit()
      except Empty:
        break
