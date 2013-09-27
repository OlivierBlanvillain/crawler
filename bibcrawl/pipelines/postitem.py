from scrapy.item import Item, Field

class PostItem(Item):
  url = Field()
  parsedBody = Field()

  post = Field()
  title = Field()
  # More to come.

  file_urls = Field()
  imagePaths = Field()

  commentFeedUrl = Field()
  commentFeed = Field()
  comments = Field()

  screenshot = Field()

