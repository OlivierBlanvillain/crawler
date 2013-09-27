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

  def __setattr__(self, key, value):
    if key in self.fields:
      super(PostItem, self).__setitem__(key, value)
    else:
      super(PostItem, self).__setattr__(key, value)

  def __getattr__(self, key):
    # This is enough because __getattr__ is a fallback...
    return self[key]
