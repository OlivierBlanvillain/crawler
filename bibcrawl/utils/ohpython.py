"""oh python...
Essential utility functions that should have been part of python core."""

from itertools import imap, ifilter, izip, chain
from functools import partial
from os.path import dirname, join

__all__ = [
  "block",
  "chain",
  "false",
  "first",
  "foreach",
  "getOrElseUpdate",
  "ifilter",
  "iflatmap",
  "imap",
  "izip",
  "let",
  "partial",
  "printf",
  "readtestdata",
  "second",
  "true",
  "tailcall",
  "tailreq",
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

def block(*_):
  """Returns the last element of a list."""
  return _[-1]

def let(var, cont):
  """Defines a variable var in cont"""
  return cont(var)

class tailreq(object):
  """Decorator for tail call elimination using trampoline. Usage:

    >>> @tailreq
    ... def fact(n, r=1):
    ...   return r if n <= 1 else tailcall(fact)(n-1, n*r)
    >>> len(str(fact(10000)))
    35660

    >>> @tailreq
    ... def even(x):
    ...   return True if x == 0 else tailcall(odd)(x - 1)
    >>> @tailreq
    ... def odd(x):
    ...   return False if x == 0 else tailcall(even)(x - 1)
    >>> odd(10000)
    False
  """
  def __init__(self, function):
    """Constructor"""
    self.function = function
  def __call__(self, *args):
    """Apply method"""
    result = self.function(*args)
    while type(result) is tailcall:
      result = result.handle()
    return result

class tailcall(object):
  """Currided definition of tail calls."""
  def __init__(self, cont):
    """Constructor"""
    self.cont = cont
    self.args = None
  def __call__(self, *args):
    """Apply method"""
    self.args = args
    return self
  def handle(self):
      """Handles the tail call"""
    # Uncomment to allow "tailcalling" non tailreq functions.
    # I personally prefer to get an error in this case.
    # if type(self.cont) is tailreq:
      return self.cont.function(*self.args)
    # else:
    #   return self.cont(*self.args)

# Test functions, here to save doctest imports...
def printf(string):
  """Print function."""
  print string

def readtestdata(path):
  """Read html blog test data"""
  if path.endswith("/"):
    path = path + "index.html"
  filename = join(dirname(__file__), "../testdata", path)
  return open(filename).read()

false = False
true = True
