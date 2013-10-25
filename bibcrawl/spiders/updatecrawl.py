"""UpdateCrawl"""

from bibcrawl.model.postitem import PostItem
from bibcrawl.utils.ohpython import *
from bibcrawl.utils.parsing import parseHTML
from bibcrawl.utils.parsing import datetimeFromStructtime
from bibcrawl.spiders.rsscrawl import RssCrawl

class UpdateCrawl(RssCrawl):
  """UpdateCrawl"""

  def __init__(self, startAt, domain, since, *args, **kwargs):
    """TODO"""
    super(self.__class__, self).__init__(startAt, domain, *args, **kwargs)
    self.since = since
    self.newRssLinks = list()

  def parse(self, response):
    """TODO"""
    postRequests = self.parseRss(response)
    self.newRssLinks = tuple((
      _.link for _ in self.contentExtractor.rssEntries
      if datetimeFromStructtime(_.published_parsed) > self.since))
    if not self.newRssLinks:
      self.logWarning("No new entries.")
    else:
      return postRequests

  def handleRssEntries(self, posts):
    """TODO"""
    return (
      PostItem(url=_.url, parsedBodies=(parseHTML(_.body),)) for _ in posts
      if _.meta["u"] in self.newRssLinks)
