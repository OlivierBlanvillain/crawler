"""oh python...
Essential utility functions that should have been part of python core."""

from itertools import imap, ifilter, izip, chain
from functools import partial

__all__ = [
  "chain",
  "first",
  "foreach",
  "getOrElseUpdate",
  "ifilter",
  "iflatmap",
  "imap",
  "izip",
  "partial",
  "printf",
  "readtestdata",
  "second",
  "typecheck",
]


def iflatmap(fun, itr):
  """Flatten map.

    >>> tuple(iflatmap(lambda _: (_, _+1, _+2), (1, 2, 6)))
    (1, 2, 3, 2, 3, 4, 6, 7, 8)

  @type  fun: function of A => list of B
  @param fun: the function to apply to each element of itr
  @type  itr: iterator of A
  @param itr: the iterator to map from
  @rtype: list of B
  @return: the flatten map of itr with fun
  """
  return chain.from_iterable(imap(fun, itr))

def foreach(fun, itr):
  """Foreach.

    >>> from pprint import pprint
    >>> foreach(pprint, (1, 2))
    1
    2

  @type  fun: function of A => Any
  @param fun: the function to apply to each element of itr
  @type  itr: iterator of A
  @param itr: the iterator to iter on
  """
  for _ in itr:
    fun(_)

def first(listOrTuple):
  """Return the first element of a list.

    >>> first((1, 2, 3))
    1

  @type  listOrTuple: list or tuple of T
  @param listOrTuple: the list or tuple
  @rtype: T
  @return: the second element of a list
  """
  return listOrTuple[0]

def second(listOrTuple):
  """Returns the second element of a list.

    >>> second((1, 2, 3))
    2

  @type  listOrTuple: list or tuple of T
  @param listOrTuple: the list or tuple
  @rtype: T
  @return: the second element of a list
  """
  return listOrTuple[1]

def typecheck(*objectZipType):
  """Typechecks (object, type) tuples.

    >>> typecheck((1, int), ("0", str))
    >>> try: typecheck((2, str))
    ... except AssertionError: pass
    ... else: fail

  @type  objectZipType: list of (object, type)
  @param objectZipType: list of object/type to typecheck
  """
  assert all(imap(lambda (_1, _2): isinstance(_1, _2), objectZipType))

def getOrElseUpdate(dictionary, key, opr):
  """If given key is already in the dictionary, returns associated value.
  Otherwise compute the value with opr, update the dictionary and return it.
  None dictionary are ignored.

    >>> d = dict()
    >>> getOrElseUpdate(d, 1, lambda _: _ + 1)
    2
    >>> print(d)
    {1: 2}

  @type  dictionary: dictionary of A => B
  @param dictionary: the dictionary
  @type  key: A
  @param key: the key
  @type  opr: function of A => B
  @param opr: the function to compute new value from keys
  @rtype: B
  @return: the value associated with the key
  """
  if dictionary is None:
    return opr(key)
  else:
    if key not in dictionary:
      dictionary[key] = opr(key)
    return dictionary[key]


# Test functions, here to save doctest imports...

def printf(string):
  "Print function."
  print string

def readtestdata(path):
  from os.path import dirname, join
  if path.endswith("/"):
    path = path + "index.html"
  filename = join(dirname(__file__), "../testdata", path)
  return open(filename).read()
