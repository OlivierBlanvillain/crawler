BlogForever crawler
===================

install:

    pip install Scrapy lxml feedparser pytest pytest-incremental
    wget PhantomJS from http://phantomjs.org/download.html
    (cd lib/; tar xjf path/to/tarball; mv * phantomjs)

run:

    python -m  bibcrawl/run

test:

    py.test

Scrapy settings:

    http://doc.scrapy.org/en/latest/topics/settings.html
