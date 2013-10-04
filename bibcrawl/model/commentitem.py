from bibcrawl.model.objectitem import ObjectItem
from scrapy.item import Item, Field

class CommentItem(ObjectItem):
  content = Field()
  author = Field()
  date = Field()
  avatarUrl = Field()
  parent = Field()
