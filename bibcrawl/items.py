from scrapy.item import Item, Field

class PostItem(Item):
  title = Field()
  link = Field()
  content = Field()