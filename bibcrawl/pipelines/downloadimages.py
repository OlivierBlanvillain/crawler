"""DownloadImages"""

from bibcrawl.pipelines.files import FilesPipeline

class DownloadImages(FilesPipeline):
  """Name wrapper with for FilesPipeline. Download images from the
  item.file_urls list and store the results (path or error) in the item.fiels.
  """
