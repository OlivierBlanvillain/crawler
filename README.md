BlogForever crawler
===================

[Final blogforever platform deployment instructions](http://blogforever.eu/wp-content/uploads/2013/10/repository-deployment-instructions.pdf)

Installation for python 2.6:

    pip install scrapy==0.18.4
    pip install lxml httplib2 feedparser selenium python-Levenshtein
    install [PhantomJS][1] to /opt/phantomjs/bin/phantomjs

Run:

    scrapy crawl newcrawl -a startat=http://www.quantumdiaries.org/
    scrapy crawl updatecrawl -a startat=http://www.quantumdiaries.org/ -a since=1388593000
Test:

    pip install pytest pytest-incremental
    py.test

[1]: http://phantomjs.org/download.html
