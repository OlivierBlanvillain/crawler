"""CommentItem"""

from bibcrawl.model.objectitem import ObjectItem
from scrapy.item import Field

class CommentItem(ObjectItem):
  """Item for blog comments."""

  content = Field()
  author = Field()
  published = Field()
  avatarUrl = Field()
  parent = Field()
