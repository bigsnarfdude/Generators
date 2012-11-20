# itertools includes a number of very helpful generators
#   for helping us transform our iterables
# here's a brief overview of some of the more useful ones

# itertools.imap
# itertools.izip
# itertools.ifilter

# itertools.{imap,izip,ifilter} are variants of
#   __builtins__.{imap,izip,ifilter} that return iterators instead of
#   materialised lists
# in Python 3, all __builtins__ that operate on sequence types
#   return iterators, so the distinction between map and imap no longer exists

# zip( *iterables ), as we know, takes pairwise elements from 
#   the provided iterables
def my_zip( *iterables ):
	iterables = [iter(x) for x in iterables]
	rv = []
	while True:
		try:
			val = [next(x) for x in iterables]
			rv.append( tuple(val) )
		except StopIteration:
			return rv

from itertools import izip
assert my_zip(    xrange(10) ,xrange(10) )  == \
       zip(       xrange(10) ,xrange(10) )  == \
       list(izip( xrange(10), xrange(10) )) == \
       [(0,0),(1,1),(2,2),(3,3),(4,4),(5,5),(6,6),(7,7),(8,8),(9,9)]

from string import ascii_lowercase
assert my_zip(    xrange(5), ascii_lowercase )  == \
       zip(       xrange(5), ascii_lowercase )  == \
       list(izip( xrange(5), ascii_lowercase )) == \
       [(0,'a'),(1,'b'),(2,'c'),(3,'d'),(4,'e')]

# map( func, iterable ), as we know, applies the function to every
#   element of the iterable and returns a list of the results
# map( func, *iterables ), follows the same pattern, but applies
#   the function to each pair of elements from zip(*iterables)
def my_map( func, *iterables ):
	rv = []
	for elements in zip(*iterables):
		rv.append( func(*elements) )
	return rv

from itertools import imap
assert my_map(    lambda x: x+2, xrange(10))  == \
       map(       lambda x: x+2, xrange(10))  == \
       list(imap( lambda x: x+2, xrange(10))) == \
       [2,3,4,5,6,7,8,9,10,11]

assert my_map(    lambda x,y: x**y, xrange(10),xrange(10))  == \
       map(       lambda x,y: x**y, xrange(10),xrange(10))  == \
       list(imap( lambda x,y: x**y, xrange(10),xrange(10))) == \
       [1, 1, 4, 27, 256, 3125, 46656, 823543, 16777216, 387420489]

# filter( pred or None, iterable ), as we know, takes a function (`predicate`)
#   and an iterable and returns elements of that iterable for which the
#   predicate is True
def my_filter( pred, iterable ):
	pred = bool if pred is None else pred
	rv = []
	for element in iterable:
		if pred( element ):
			rv.append( element )
	return rv

iseven = lambda x: x % 2 == 0
isodd  = lambda x: x % 2 != 0

from itertools import ifilter
assert my_filter(    iseven, xrange(10) )  == \
       filter(       iseven, xrange(10) )  == \
       list(ifilter( iseven, xrange(10) )) == \
       [0, 2, 4, 6, 8]
assert my_filter(    isodd, xrange(10) )  == \
       filter(       isodd, xrange(10) )  == \
       list(ifilter( isodd, xrange(10) )) == \
       [1, 3, 5, 7, 9]

assert my_filter(    None, [False,True,0,1,0.0,1.0,'','a',[],[0],{},{0}])  == \
       filter(       None, [False,True,0,1,0.0,1.0,'','a',[],[0],{},{0}])  == \
       list(ifilter( None, [False,True,0,1,0.0,1.0,'','a',[],[0],{},{0}])) == \
       [True,1,1.0,'a',[0],{0}]

# itertools.tee

# tee is like the coreutils command line utility, `tee`
#   take an iterable (stream) and return n independent iterables
# this is useful with generators, since yielding values from a generator
#   will exhaust the generator

gen = (x for x in xrange(10))
assert list(gen) == list(xrange(10)) == [0,1,2,3,4,5,6,7,8,9]
assert list(gen) == [] # exhausted

gen = (x for x in xrange(10))

from itertools import tee
gen1, gen2 = tee(gen,2)
assert list(gen1) == list(xrange(10)) == [0,1,2,3,4,5,6,7,8,9]
assert list(gen1) == [] # exhausted
# but gen2 is independent of gen1!
assert list(gen2) == list(xrange(10)) == [0,1,2,3,4,5,6,7,8,9]
assert list(gen2) == [] # exhausted

# itertools.groupby

# groupby takes a sorted iterable and forms groups (similar to the SQL
#   GROUP BY command)

from collections import namedtuple
Employee = namedtuple( 'Employee', 'name position salary' )
employees = ( Employee('janet',    'manager', 200000),
              Employee('john',     'manager', 500000),
              Employee('jim',      'peon',     65000),
              Employee('patricia', 'manager', 300000), )

# sort by position
# this is a necessary first step before using groupby()
# groupby will create groups only when the key's value changes
#   similar to how the command line utility `uniq` works
# this allows groupby to operate on infinite iterables and
#   iterables that we do not want to materialise
employees = list(sorted(employees, key=lambda e: e.position))

# group by position

# groupby returns an iterable of which each element is 
#   the key value and another iterable which contains all of the elements
# as a consequence, we have to do a little bit of work to materialise
#   the results of groupby() into something we can check
from itertools import groupby
assert [(k,set(v)) for k,v in groupby( employees, lambda e: e.position )] == \
       [('manager', {Employee('janet',    'manager', 200000),
                     Employee('john',     'manager', 500000),
                     Employee('patricia', 'manager', 300000)} ),
        ('peon',    {Employee('jim',      'peon',     65000)} )]

# itertools.product

# product(*iterables, repeat) gives the cartesian product of the provided
#   iterables
# the repeat parameter allows us to easily compute the cartesian product
#   of an iterable and itself
from itertools import product
assert list(product(xrange(3),'abcd')) == \
       [(0,'a'),(0,'b'),(0,'c'),(0,'d'),
        (1,'a'),(1,'b'),(1,'c'),(1,'d'), 
        (2,'a'),(2,'b'),(2,'c'),(2,'d')]

assert list(product(xrange(3),repeat=2)) == \
       [(a,b) for a in xrange(3) for b in xrange(3)] == \
       [(0,0),(0,1),(0,2),
        (1,0),(1,1),(1,2),
        (2,0),(2,1),(2,2)]

# itertools.combinations
# itertools.combinations_with_replacement
# itertools.permutations

# combinations, combinations_with_replacement, and permutations
#   provide possible orderings for an iterable
from itertools import combinations
assert list(combinations('abcd',2)) == \
       [('a','b'),('a','c'),('a','d'),('b','c'),('b','d'),('c','d')]

from itertools import combinations_with_replacement
assert list(combinations_with_replacement('abcd',2)) == \
       [('a','a'),('a','b'),('a','c'),('a','d'),
        ('b','b'),('b','c'),('b','d'),
        ('c','c'),('c','d'),
        ('d','d')]

from itertools import permutations
assert list(''.join(x) for x in permutations('abcd')) == \
       ['abcd', 'abdc', 'acbd', 'acdb', 'adbc', 'adcb',
        'bacd', 'badc', 'bcad', 'bcda', 'bdac', 'bdca',
        'cabd', 'cadb', 'cbad', 'cbda', 'cdab', 'cdba',
        'dabc', 'dacb', 'dbac', 'dbca', 'dcab', 'dcba']

assert list(''.join(x) for x in permutations('abcd',2)) == \
       ['ab', 'ac', 'ad',
        'ba', 'bc', 'bd',
        'ca', 'cb', 'cd',
        'da', 'db', 'dc']

# we can use these generators to create some simple but useful
#   other combinatorial generators

# the powerset yields all of the possible combinations of 
#   any number of elements from a given iterable
# this function will consume a generator
from itertools import combinations
def powerset( iterable ):
	iterable = list(iterable)
	for r in xrange(1,len(iterable)+1):
		for x in combinations( iterable, r ):
			yield x

assert [''.join(x) for x in powerset('abc')] == \
       ['a','b','c','ab','ac','bc','abc'] 

# all permutations is all of the possible permutations
#   of any number of elements from the given iterable
# this is different from the powerset in that the result is 
#   ordered
# this function will consume a generator
from itertools import permutations
def all_permutations( iterable ):
	iterable = list(iterable)
	for r in xrange(1,len(iterable)+1):
		for x in permutations( iterable, r ):
			yield x

assert [''.join(x) for x in all_permutations('abc')] == \
       [ 'a','b','c',
         'ab','ac','ba','bc','ca','cb',
         'abc','acb','bac','bca','cab','cba' ]
