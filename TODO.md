TOTO:
----

newcrawl:

- Contentextractor.py: Make all the pages votes, not only the first one
- Parsing.py: Build relative xPath is id and class selectors fail
- Use buildin Logs


updatecrawl:

- Schedule only from feed, reuse with full pipeline


blogmonitor:

- Detect and use global comment feeds

    - /feeds/comments/default
    - /comments/feed/

- Persistant blog info management
- Check for updates, fire scrapyd jobs
