"""Scrapy settings"""

# See http://doc.scrapy.org/en/0.18/topics/settings.html#topics-settings-ref
# for the complete list of scrapy

ITEM_PIPELINES = {
  'bibcrawl.pipelines.renderjavascript.RenderJavascript': 300,
  'bibcrawl.pipelines.processhtml.ProcessHtml': 400,
  'bibcrawl.pipelines.downloadimages.DownloadImages': 500,
  # 'bibcrawl.pipelines.downloadfeeds.DownloadFeeds': 600,
  'bibcrawl.pipelines.extractcomments.ExtractComments': 700,
  'bibcrawl.pipelines.backendpropagate.BackendPropagate': 800,
}
FILES_STORE    = 'img'
SPIDER_MODULES = ['bibcrawl.spiders']
PHANTOMJS_PATH = '/opt/phantomjs/bin/phantomjs'
