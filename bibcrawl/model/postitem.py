from bibcrawl.model.objectitem import ObjectItem
from scrapy.item import Item, Field

class PostItem(ObjectItem):
  url = Field()
  parsedBody = Field()

  content = Field()
  title = Field()
  # More to come.

  file_urls = Field()
  files = Field()

  commentFeedUrls = Field()
  commentFeed = Field()
  comments = Field()

  screenshot = Field()
