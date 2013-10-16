import unittest
from bibcrawl.units.mockserver import MockServer
from bibcrawl.utils.contentextractor import ContentExtractor
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

  def assertContains(self, string, substring):
    self.assertEqual(substring in string, True)

  def testScreenShot(self):
    item = PostItem(url="http://localhost:8000/example.com")
    self.pipeline.saveScreenshot(item, self.driver)
    self.assertEqual(item.screenshot, "screen/"
      "0aa21e9d723c0ef4492126d3c4305c3cd82f39b6.png")

  # /!\ Online test case /!\
  def testDisqusCommentsClicks(self):
    item = PostItem(url="http://korben.info/hadopi-faut-il-vraiment-arreter-"
      "de-telecharger.html")
    self.driver.get(item.url)
    self.assertGreaterEqual(len(disqusComments(self.driver)), 108)

  # /!\ Online test case /!\
  def testDisqusContent(self):
    item = PostItem(url="http://docs.scala-lang.org/tutorials/scala-for-"
      "java-programmers.html")
    self.driver.get(item.url)

    comments = disqusComments(self.driver)
    self.assertGreaterEqual(len(comments), 23)

    self.assertEqual(comments[0].author, u"Lars St\xf8ttrup Nielsen")
    self.assertContains(comments[0].content, u"I managed to get through this")
    self.assertEqual(comments[0].published, u"Wednesday, July 4 2012 11:14 PM")
    self.assertEqual(comments[0].parent, None)
    foundChild = False
    for c in comments:
      self.assertTrue(c.author)
      self.assertTrue(c.content)
      self.assertTrue(c.published)
      if c.parent is comments[1]:
        foundChild = True
    self.assertTrue(foundChild)

  # /!\ Online test case /!\
  def testLivefyreClicks(self):
    item = PostItem(url="http://techcrunch.com/2013/09/26/iphone-5s-and-iphone-5c/")
    self.driver.get(item.url)
    self.assertGreaterEqual(len(livefyreComments(self.driver)), 105)

  # /!\ Online test case /!\
  def testAAALivefyreContent(self):
    item = PostItem(url="http://techcrunch.com/2013/10/04/skype-will-finally-start-syncing-chat-messages-across-devices/")
    self.driver.get(item.url)

    comments = livefyreComments(self.driver)
    print comments

    self.assertEqual(comments[0].author, u"PaulSalo")
    self.assertContains(comments[0].content, u"Need a reliable history")
    self.assertEqual(comments[0].parent, None)
    foundChild = False
    for c in comments:
      self.assertTrue(c.author)
      self.assertTrue(c.content)
      self.assertTrue(c.published)
      if c.parent is not None and c.parent.author == u"Will6":
        foundChild = True
    self.assertTrue(foundChild)

  # /!\ Online test case /!\
  def testFullWorkflow(slef):
    pass

