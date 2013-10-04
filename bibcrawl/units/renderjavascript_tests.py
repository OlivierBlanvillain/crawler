import unittest
from bibcrawl.units.mockserver import MockServer
from bibcrawl.spiders.contentextractor import ContentExtractor
from bibcrawl.pipelines.renderjavascript import RenderJavascript
from bibcrawl.pipelines.renderjavascript import disqusComments
from bibcrawl.pipelines.renderjavascript import livefyreComments
from bibcrawl.model.postitem import PostItem

from tempfile import mkdtemp
from shutil import rmtree
class RenderJavascriptTests(unittest.TestCase):
  def setUp(self):
    self.tempdir = mkdtemp()
    self.pipeline = RenderJavascript(self.tempdir)
    self.driver = self.pipeline.webdrivers.acquire()
    self.mockserver = MockServer()
    self.mockserver.__enter__()

  def tearDown(self):
    rmtree(self.tempdir)
    self.pipeline.webdrivers.release(self.driver)
    self.mockserver.__exit__(None, None, None)

  def testPhantomJS(self):
    pass

  def testScreenShot(self):
    item = PostItem(url="http://localhost:8000/example.com")
    self.pipeline.saveScreenshot(item, self.driver)
    self.assertEqual(item.screenshot, "screen/"
      "0aa21e9d723c0ef4492126d3c4305c3cd82f39b6.png")

  # /!\ Online test case /!\
  def testDisqusComments(self):
    item = PostItem(url="http://docs.scala-lang.org/tutorials/scala-for-"
      "java-programmers.html")
    self.driver.get(item.url)
    self.assertGreaterEqual(len(disqusComments(self.driver)), 23)

  # /!\ Online test case /!\
  def testDisqusCommentsClicks(self):
    item = PostItem(url="http://korben.info/hadopi-faut-il-vraiment-arreter-"
      "de-telecharger.html")
    self.driver.get(item.url)
    self.assertGreaterEqual(len(disqusComments(self.driver)), 108)
