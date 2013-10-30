blogforever-crawler
===================

Blog crawler for the blogforever project.

install:

    pip install lxml, feedparser, goose-extractor, boilerpipe, readability-lxml


run:

    python -m  bibcrawl/run


test:

    nosetests --verbose --with-doctest --with-coverage --cover-package bibcrawl
