"""Name wrapper with for FilesPipeline."""

from bibcrawl.pipelines.files import FilesPipeline

class DownloadImages(FilesPipeline):
  """Download images from the item.file_urls list and store the results (path
  or error) in the item.fiels.
  """
