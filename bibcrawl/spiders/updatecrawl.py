"""UpdateCrawl"""

from bibcrawl.model.postitem import PostItem
from bibcrawl.utils.ohpython import *
from bibcrawl.utils.parsing import parseHTML
from bibcrawl.utils.parsing import datetimeFromStructtime
from bibcrawl.spiders.rsscrawl import RssCrawl
from datetime import datetime
class UpdateCrawl(RssCrawl):
  name = "updatecrawl"

  def __init__(self, startat, since):
    """Instantiate an updatecrawl spider for a given start url and since date.

    @type  startat: string
    @param startat: the web feed to the crawl
    @type  since: string
    @param since: the unix timestamp after which content is considered new
    """
    super(self.__class__, self).__init__(startat)
    self.since = datetime.fromtimestamp(int(since))
    self.newRssLinks = list()

  def parseRss(self, response):
    """Extract the new entry Requests from the RSS feed.

    @type response: scrapy.http.response.html.HtmlResponse
    @param response: the RSS feed
    @rtype: generator of scrapy.http.request.Request
    @return: the new entry Requests
    """
    postRequests = super(UpdateCrawl, self).parseRss(response)
    self.newRssLinks = tuple((
      _.link for _ in self.contentExtractor.rssEntries
      if datetimeFromStructtime(_.published_parsed) > self.since))
    if not self.newRssLinks:
      self.logWarning("No new entries.")
    else:
      return postRequests

  def handleRssEntries(self, posts):
    """Process the new RSS entry Responses.

    @type posts: scrapy.http.posts.html.HtmlResponse
    @param posts: the RSS entries Responses
    @rtype: generator of scrapy.item.Item
    @return: the next items to process
    """
    return (
      PostItem(url=_.url, parsedBodies=(parseHTML(_.body),)) for _ in posts
      if _.meta["u"] in self.newRssLinks)
