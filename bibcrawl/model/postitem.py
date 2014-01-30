"""PostItem"""

from bibcrawl.model.objectitem import ObjectItem
from scrapy.item import Field

class PostItem(ObjectItem):
  """Item for blog post."""

  url = Field()
  parsedBodies = Field()

  content = Field()
  title = Field()
  author = Field()
  # More to come.

  file_urls = Field()
  files = Field()

  commentFeedUrls = Field()
  commentFeed = Field()
  comments = Field()

  screenshot = Field()
