# BlogForever crawler

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


### TODO:

Add to the DB, per blog

- link to web-feed
- latest etag of this feed
- date of last crawl (unix format)

Blog monitor algo:

    if isFresh, start an updatecrawl with last crawl date
    otherwise we are fine for this blog.


### Tree with docstrings:

    bibcrawl
    ├── model
    │   ├── commentitem.py: Blog comment Item
    │   ├── objectitem.py: Super class of comment and post item
    │   └── postitem.py: Blog post Item
    ├── pipelines
    │   ├── backendpropagate.py: Saves the item in the back-end
    │   ├── downloadfeeds.py: Downloads comments web feed
    │   ├── downloadimages.py: Download images
    │   ├── extractcomments.py: Extracts all comments from html using the comment feed
    │   ├── files.py: Files pipeline back-ported to python 2.6
    │   ├── processhtml.py: Process html to extract article, title and author
    │   └── renderjavascript.py: Renders the original page with PhantomJS and takes a screenshot
    ├── spiders
    │   ├── newcrawl.py: Entirely crawls a new blog
    │   ├── rsscrawl.py: Super class of new and update crawl
    │   └── updatecrawl.py: Partialy crawls a blog for new content of the web feed
    ├── utils
    │   ├── contentextractor.py: Extracts the content of blog posts using a RSS feed
    │   ├── ohpython.py: Essential functions that should have been part of python core
    │   ├── parsing.py: Parsing functions
    │   ├── priorityheuristic.py: Priority heuristic for page download, favors page with links to blog posts
    │   ├── stringsimilarity.py: Dice's coefficient similarity function
    │   └── webdriverpool.py: Pool of PhantomJS processes to parallelize page rendering
    ├── blogmonitor.py: Queries the database and starts new and update crawls when needed, to be called periodically
    └── settings.py: Scrapy settings
