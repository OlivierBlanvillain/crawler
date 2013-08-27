"""Moke Server, made for simple offline testing. Usage:

  >>> with MockServer("korben.info", 8080):
  >>>   from urllib2 import urlopen
  >>>   len( urlopen('http://localhost:8080') )
  10
"""
class MockServer(object):
  """Moke Server Context"""
  def __init__(self, page, port):
    self.page = page
    self.port = port

  def __enter__(self):
    """Starts a MockServer in a new process."""
    self.proc = Popen([sys.executable, '-u', '-m', 'bibcrawl.tests.mockserver', page, port],
                      stdout=PIPE)
    self.proc.stdout.readline()

  def __exit__(self, exc_type, exc_value, traceback):
    """Starts a MockServer in a new process."""
    self.proc.kill()
    self.proc.wait()
    time.sleep(0.2)

class Simple(resource.Resource):
  isLeaf = True
  def render_GET(self, request):
    return "<html>Hello, world!</html>"

if __name__ == "__main__":
  site = server.Site(Simple())
  reactor.listenTCP(8123, site)
  reactor.run()
