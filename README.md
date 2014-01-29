BlogForever crawler
===================

install:

    pip install scrapy==0.18.4
    pip install lxml feedparser pytest pytest-incremental
    wget PhantomJS from http://phantomjs.org/download.html
    (cd lib/; tar xjf path/to/tarball; mv * phantomjs)

run:

    scrapy crawl NewCrawl -a startAt="http://www.quantumdiaries.org/"

test:

    py.test
