"BlogMonitor"

from bibcrawl.utils.ohpython import *
from httplib2 import Http

#  trigger(since, BlogFeeds, CommentFeeds)

def isFresh(url, etag):
  """Returns True if the resource at the given url  was modified.

    >>> e = first(Http().request("http://www.quantumdiaries.org/feed/"))["etag"]
    >>> isFresh("http://www.quantumdiaries.org/feed/", e)
    False
    >>> isFresh("http://www.quantumdiaries.org/feed/", '"slkdfjsldkjf"')
    True

  @type  url: string
  @param url: the page to download
  @type  etag: string
  @param etag: the etag of the last request
  @rtype: boolean
  @return: True if the resource was modified
  """
  (resp, _) = Http().request(url, "HEAD", headers={ 'If-None-Match': etag })
  return resp.status != 304

def getAllBlogs():
  """Returns all the managed blogs.

  @rtype: list of Blog
  @return: all the managed blogs
  """
  pass

class Blog(object):
  """Blog"""
  def __init__(self, starturl, feedurl, etag, lastupdate):
    """Create a Blog instance

    @type  starturl: string
    @param starturl: the starturl
    @type  feedurl: string
    @param feedurl: the feedurl
    @type  etag: string
    @param etag: the etag
    @type  lastupdate: string
    @param lastupdate: the lastupdate
    """
    self.starturl = starturl
    self.feedurl = feedurl
    self.etag = etag
    self.lastupdate = lastupdate

  def copy(self, lastupdate):
    """Returns a copy of this Blog with a new lastupdate.

    @type  lastupdate: string
    @param lastupdate: the new lastupdate
    @rtype: Blog
    @return: the copy of this Blog
    """
    return Blog(self.starturl, self.feedurl, self.etag, lastupdate)
