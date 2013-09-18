from scrapy.item import Item, Field

class PostItem(Item):
  url = Field()
  body = Field()

  file_urls = Field()
  imagePaths = Field()

  commentFeedUrl = Field()
  commentFeed = Field()
  comments = Field()

  screenshot = Field()

