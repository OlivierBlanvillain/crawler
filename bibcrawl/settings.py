SPIDER_MODULES = ['bibcrawl.spiders']

ITEM_PIPELINES = [
    'bibcrawl.pipelines.renderjavascript.RenderJavascript',
    'bibcrawl.pipelines.processhtml.ProcessHtml',
    'bibcrawl.pipelines.downloadimages.DownloadImages',
    'bibcrawl.pipelines.downloadfeeds.DownloadFeeds',
    'bibcrawl.pipelines.extractcomments.ExtractComments',
    'bibcrawl.pipelines.backendpropagate.BackendPropagate']

HTTPCACHE_STORAGE = 'scrapy.contrib.httpcache.FilesystemCacheStorage'
HTTPCACHE_ENABLED = True
FILES_STORE = 'img'
CONCURRENT_ITEMS = 10

# SPIDER_MODULES = [ 'bibcrawl.spiders.newcrawl', 'bibcrawl.spiders', 'bibcrawl' ]
