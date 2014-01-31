"""Super class of comment and post item"""

from scrapy.item import Item

class ObjectItem(Item):
  """Extends Scrapy Item interface to be usable with the standard object
  attribute notation.

    >>> from scrapy.item import Field
    >>> class I(ObjectItem):
    ...   myField = Field()
    >>> i = I()
    >>> i.myField = 1
    >>> i.myField
    1
    >>> try:
    ...   i.notAField
    ... except KeyError:
    ...   pass
    ... else:
    ...   fail
  """

  def __setattr__(self, key, value):
    """Sets a fild of the item using object attribute notation."""
    if key in self.fields:
      super(ObjectItem, self).__setitem__(key, value)
    else:
      super(ObjectItem, self).__setattr__(key, value)

  def __getattr__(self, key):
    """Gets a fild of the item using object attribute notation."""
    # This is enough because __getattr__ is a fallback...
    return self[key]
