ITEM_PIPELINES = {
  'bibcrawl.pipelines.renderjavascript.RenderJavascript': 300,
  'bibcrawl.pipelines.processhtml.ProcessHtml': 400,
  # 'bibcrawl.pipelines.downloadimages.DownloadImages': 500,
  'bibcrawl.pipelines.downloadfeeds.DownloadFeeds': 600,
  'bibcrawl.pipelines.extractcomments.ExtractComments': 700,
  'bibcrawl.pipelines.backendpropagate.BackendPropagate': 800,
}
FILES_STORE         = "img"
CONCURRENT_ITEMS    = 1
STATS_DUMP          = False
CONCURRENT_REQUESTS = 1
CONCURRENT_REQUESTS_PER_DOMAIN = 1
CONCURRENT_REQUESTS_PER_IP = 1
SPIDER_MODULES = ['bibcrawl.spiders']
