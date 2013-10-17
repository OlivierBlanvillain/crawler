#     >>> with MockServer():
#     ...   pages = (parseHTML(dl("disqus.com/embed/comments/")), parseHTML(
#     ...     dl("korben.info/hadopi-faut-il-vraiment-arreter-de-telecharger"
#     ...     ".html")))
#     ...   comments = commentsFromFeed(parse(dl("disqus.com/embed/comments/")))
#     ...   cmts = commentsHtmlExtraction(comments, pages, debug=True)
#     ("//div[@class='post']", "//div[@class='post-message']", \
# "//div[@class='author']", "//div[@class='post-meta']/a",)
