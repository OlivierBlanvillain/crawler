"""OutPropagate"""
from bibcrawl.utils.fixbadunicode import fix_bad_unicode
from bibcrawl.utils.stringsimilarity import cleanTags

class OutPropagate(object):
  """
  @type  item: bibcrawl.model.postitem.PostItem
  @param item: the item to process
  @type  spider: scrapy.spider.BaseSpider
  @param spider: the spider that emitted this item
  @rtype: bibcrawl.model.postitem.PostItem
  @return: the processed item
  """
  def process_item(self, item, spider):
    import codecs
    path = "out/" + item.url.replace("/", "{")
    spider.logInfo(path)
    nicecontent = fix_bad_unicode(cleanTags(item.content))
    with codecs.open(path , "w", encoding="utf-8") as out:
      out.write(nicecontent)
