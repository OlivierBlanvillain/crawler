import lxml.html, lxml.html.clean
from lxml.html.clean import Cleaner

# http://en.wikibooks.org/wiki/Algorithm_Implementation/Strings/
# Dice's_coefficient
def dice_coefficient(a, b):
    """dice coefficient 2nt/na + nb."""
    a_bigrams = set(a)
    b_bigrams = set(b)
    print "a_bigrams"
    print a_bigrams
    print "b_bigrams"
    print b_bigrams
    print ""
    overlap = len(a_bigrams & b_bigrams)
    return overlap * 2.0/(len(a_bigrams) + len(b_bigrams))

def dice_coefficient2(a, b):
    """dice coefficient 2nt/na + nb."""
    if not len(a) or not len(b): return 0.0
    if len(a) == 1:  a=a+u'.'
    if len(b) == 1:  b=b+u'.'

    a_bigram_list=[]
    for i in range(len(a)-1):
      a_bigram_list.append(a[i:i+2])
    b_bigram_list=[]
    for i in range(len(b)-1):
      b_bigram_list.append(b[i:i+2])

    a_bigrams = set(a_bigram_list)
    b_bigrams = set(b_bigram_list)
    overlap = len(a_bigrams & b_bigrams)
    dice_coeff = overlap * 2.0/(len(a_bigrams) + len(b_bigrams))
    return dice_coeff

# http://stackoverflow.com/questions/653157/a-better-similarity-ranking-
# algorithm-for-variable-length-strings
def get_bigrams(string):
    '''
    Takes a string and returns a list of bigrams
    '''
    s = string.lower()
    return [s[i:i+2] for i in xrange(len(s) - 1)]

def string_similarity(str1, str2):
    '''
    Perform bigram comparison between two strings
    and return a percentage match in decimal form
    '''
    pairs1 = get_bigrams(str1)
    pairs2 = get_bigrams(str2)
    union  = len(pairs1) + len(pairs2)
    hit_count = 0
    for x in pairs1:
        for y in pairs2:
            if x == y:
                hit_count += 1
                break
    return (2.0 * hit_count) / union

def get_bigrams2(s):
    '''
    Takes a string and returns a list of bigrams
    '''
    return { s[i:i+2] for i in xrange(len(s) - 1) }

def string_similarity2(str1, str2):
    '''
    Perform bigram comparison between two strings
    and return a percentage match in decimal form
    '''
    pairs1 = get_bigrams2(str1)
    pairs2 = get_bigrams2(str2)
    intersection = pairs1 & pairs2
    return (2.0 * len(intersection)) / (len(pairs1) + len(pairs2))

from Levenshtein import ratio # as stringSimilarity
from Levenshtein import jaro # as stringSimilarity

cleanTag = lambda string: (
  Cleaner(allow_tags=[''], remove_unknown_tags=False).clean_html(string or u"dummy")
)
# (
#   lxml.etree.tostring(
#     lxml.html.clean.Cleaner(
#       allow_tags=[''],
#       remove_unknown_tags = False
#     ).clean_html(
#       lxml.html.fromstring(
#         (string or "dummy")))))

def stringSimilarity (str1, str2):
  # print "<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<"
  # print cleanTag(str2)
  # print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
  return string_similarity2(
    # filter(lambda _: _.isalnum(), str1),
    # filter(lambda _: _.isalnum(), str2))
    cleanTag(str1), cleanTag(str2))
