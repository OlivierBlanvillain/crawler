"""UpdateCrawl"""

from bibcrawl.model.postitem import PostItem
from bibcrawl.utils.ohpython import *
from bibcrawl.utils.parsing import parseHTML
from bibcrawl.utils.parsing import datetimeFromStructtime
from bibcrawl.spiders.rsscrawl import RssCrawl

class UpdateCrawl(RssCrawl):
  """UpdateCrawl"""
  name = "UpdateCrawl"

  def __init__(self, domain, since, *args, **kwargs):
    """TODO"""
    super(UpdateCrawl, self).__init__(domain, *args, **kwargs)
    self.since = since

  def handleRssPosts(self, posts):
    """TODO"""
    newRssLinks = set(imap(
      lambda _: _.link,
      ifilter(
        lambda _: datetimeFromStructtime(_.published_parsed) > self.since,
        self.contentExtractor.rssEntries)))
    return imap(
      lambda _: PostItem(url=_.url, parsedBodies=(parseHTML(_.body),)),
      ifilter(
        lambda _: _.meta["u"] in newRssLinks,
        posts))
