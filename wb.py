from selenium import webdriver
from selenium.webdriver.support import ui
from time import sleep, time
from selenium.common.exceptions import ElementNotVisibleException

url, iframeXPath, loadMoarXPath = (
  "http://docs.scala-lang.org/tutorials/scala-for-java-programmers.html",
  # "http://korben.info/hadopi-faut-il-vraiment-arreter-de-telecharger.html",
  "//iframe[@id='dsq1']",
  "//div[@class='load-more']/a"
)

# url, iframeXPath, loadMoarXPath = (
#   "http://techcrunch.com/2013/09/11/the-iphone-5s-class/",
#   None,
#   "//div[@class='fyre-stream-more']"
# )

# d = webdriver.Firefox()
d = webdriver.PhantomJS("./lib/phantomjs/bin/phantomjs")
d.get(url)

if iframeXPath:
  d.switch_to_frame(d.find_element_by_xpath(iframeXPath))

timeout = time() + 5
try:
  while time() < timeout:
    # d.execute_script("$('.fyre-stream-more').click()")
    d.find_element_by_xpath(loadMoarXPath).click()
except ElementNotVisibleException:
  pass

d.save_screenshot('screen.png') # get_screenshot_as_png()
d.switch_to_default_content()

# print (d.page_source).encode('utf-8')
d.quit()


# Download files with PhantomJS is WIP:
# https://github.com/ariya/phantomjs/pull/11484
# And seems to be possible with Firefox: https://code.google.com/
# p/selenium/wkii/RubyBindings#Tweaking_Firefox_preferences
