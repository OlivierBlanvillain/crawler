blogforever-crawler
===================

Blog crawler for the blogforever project.

run:

    python -m  bibcrawl/run


test:

    nosetests --with-doctest bibcrawl


continuous integration setup:

    nodemon -e .py --exec "sudo nosetests --verbose --rednose --with-doctest --with-coverage --failed --cover-package bibcrawl"
