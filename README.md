BlogForever crawler
===================

[Final blogforever platform deployment instructions](http://blogforever.eu/wp-content/uploads/2013/10/repository-deployment-instructions.pdf)

install:

    pip install scrapy==0.18.4
    pip install lxml httplib2 feedparser pytest pytest-incremental selenium
    wget PhantomJS from http://phantomjs.org/download.html
    (cd lib/; tar xjf path/to/tarball; mv * phantomjs)

run:

    scrapy crawl NewCrawl -a startAt="http://www.quantumdiaries.org/"

test:

    py.test
