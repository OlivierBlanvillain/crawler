#!/bin/sh

for d in $(cat ../blogforever-crawler-publication/dataset/bloglist); do sudo python -m bibcrawl/run $d; done
