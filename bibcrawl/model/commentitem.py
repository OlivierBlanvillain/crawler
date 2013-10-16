from bibcrawl.model.objectitem import ObjectItem
from scrapy.item import Item, Field

class CommentItem(ObjectItem):
  content = Field()
  author = Field()
  published = Field()
  avatarUrl = Field()
  parent = Field()
