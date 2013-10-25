"""MockServer"""


from os import chdir
from os.path import abspath, dirname, join
from SimpleHTTPServer import SimpleHTTPRequestHandler
from SocketServer import TCPServer
from subprocess import Popen, PIPE
from urllib2 import urlopen
import sys, time

class MockServer(object):
  """Moke Server, made for simple offline testing. Usage:

    >>> from urllib2 import urlopen
    >>> with MockServer():
    ...   len(urlopen("http://localhost:8000/example.com").read())
    1344
  """
  def __init__(self):
    self.proc = None

  def __enter__(self):
    """Starts a MockServer listening for port 8000 on a new process."""
    self.proc = Popen(
        [sys.executable, "-u", "-m", "bibcrawl.units.mockserver"],
        stdout=PIPE)
    self.proc.stdout.readline()

  def __exit__(self, exc_type, exc_value, traceback):
    """Stops the MockServer."""
    self.proc.kill()
    self.proc.wait()
    time.sleep(0.2)

class NullStrea(object):
  """Null Stream"""
  def write(self, _):
    """Unit write method"""
    pass

def run():
  """ Serves"""
  chdir(join(abspath(dirname(__file__)), "blogs"))
  TCPServer.allow_reuse_address = True
  httpd = TCPServer(("", 8000), SimpleHTTPRequestHandler)
  print "I am here to serve you."
  sys.stdout = NullStrea()
  sys.stderr = NullStrea()
  httpd.serve_forever()

def dl(url):
  """Donwload a page from the MockServer."""
  # print "http://localhost:8000/{}".format(url)
  return urlopen("http://localhost:8000/{}".format(url)).read()

if __name__ == "__main__":
  run()

class PrintSpider:
  def logDebug(self, string):
    print string

  def logInfo(self, string):
    print string

  def logWarning(self, string):
    print string

  def logError(self, string):
    print string

  def logCritical(self, string):
    print string

def printer(string):
  print string
