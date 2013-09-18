class DebugPrint(object):
  def process_item(self, item, spider):
    # print("")
    print("> " + item["url"])
    return item
