#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
from __future__ import division

__title__  = 'Generators and Co-Routines for Stream Data Processing'
__author__ = 'V James Powell <vpowell@gmail.com>'

# ABSTRACT
# this handout discusses the use of generator features in Python
#   for data processing using a "stream" metaphor
# it discusses the distinction between generators, iterators, generator
#   expressions and coroutines, including syntax and concepts
# it discusses the basic metaphor behind a "stream" processing code flow
# it also discusses optimisation techniques that this allows

# GOALS
# for novices, I'd like to introduce y'all to the concept of 
#   generators in a very rigourous fashion (and in a fashion that
#   most tutorials do not discuss)
#   I'd also like to introduce the topic of coroutines
# for advanced users, I'd like to discuss some optimisation proposals
#   for problems that are modelled using generators and also discuss
#   generators as one of the fundamental semantic pieces
#   in Python (i.e., the primacy of __call__ and __iter__)
#   also, I'd like to discuss a hard problem (how to write a function
#   that is guaranteed not to exhaust a generator)

# SYNTAX
# from a syntax perspective, when we talk about generaotrs in Python, we're
#   generally referring to:
#   1. iterator/generator protocol (an interface consisting of .next/__next__
#      and, optionally, .send and .throw)
#   2. generator yield-syntax
#   3. generator expression syntax

# SYNTAX // ITERATOR PROTOCOL

# an iterator in Python is any object that defines an .__iter__() method and a
#   .next method

# note: in Python3, the .next method is called .__next__

# these two methods are a fundamental part of the Python object data model:
#   .__iter__() corresponds to `getiterfunc tp_iter` on PyTypeObject
#   .next() corresponds to `iternextfunc tp_iternext` on PyTypeObject

# these two methods also correspond to the __builtin__ functions
#   iter() for .__iter__()
#   next() for .next()/.__next__()

# trivial iterator implements the most trivial iterator object
#   this is an object that represents an infinite sequence of None values

class trivial_iterator(object):
	def __iter__(self): return self
	def __next__(self): return None
	next = __next__

# trivial_iterator is an Iterator type, as it has both a .next and .__iter__()
#   method
from collections import Iterator
assert issubclass(trivial_iterator, Iterator)

# we can iterate over it using for-loop syntax
for x in trivial_iterator():
	pass 
	break

# let's modify the example slightly:

# our trivial iterator now has some internal notion of state
# this state is just a counter that counts from 0 up to 5
# once this internal counter hits 5, the iterator raises a StopIteration
#   which is how we signal there are no more values
class trivial_iterator(object):
	def __init__(self):
		self.state = 0
	def __iter__(self): return self
	def __next__(self):
		if self.state == 5: 
			raise StopIteration()
		self.state += 1
		return None
	next = __next__

# we can still iterate over the above, and it will now terminate after
#   yielding 5 None values
for x in trivial_iterator():
	pass

# we can also see that we can pass it to any function that iteratos internally:
assert set(trivial_iterator()) == set([None])
assert list(trivial_iterator()) == [None, None, None, None, None] 
assert tuple(trivial_iterator()) == (None, None, None, None, None)

# SYNTAX // FOR LOOPS

# we can look at our for-loop syntax as actually looking something like this:

for x in trivial_iterator():
	pass

# is equivalent to
try:
	iterable = iter(trivial_iterator()) # calls our .__iter__() method
	while True:
		x = next(iterable) # calls our .next()/.__next__() method
		pass
except StopIteration:
	pass

# SYNTAX // ITERATORS vs ITERABLES

# this suggests to us something very important:
#   iterators are iterable objects plus a bit of state to track where
#   you are in the iteration

# in other words, a list [1,2,3,4] is an Iterable but not an Iterator
# it's not an Iterator, because there's no place for us to store
#   information about where we are in the iteration
# a trivial listiterator would look like:
class listiterator(object):
	def __init__(self, list_obj):
		self.list_obj = list_obj
		self.idx = 0
	def __iter__(self):
		return self
	def __next__(self):
		if self.idx > len(self.list_obj):
			raise StopIteration()
		rv = self.list_obj[self.idx]
		self.idx += 1
		return rv
	next = __next__

assert next(listiterator([1,2,3])) == 1

# SYNTAX // GENERATORS

# now, let's consider an iterator that takes a function and repeatedly calls
#   it to provide values

class generatorlike(object):
	def __init__(self, func, state=None):
		self.state = None
		self.func = func
	def __iter__(self):
		return self
	def __next__(self):
		self.state = self.func(self.state)
		return self.state
	next = __next__

def count(x):
	x = 0 if x is None else x+1
	if x == 3: raise StopIteration() # need a stop condition
	return x

assert list(generatorlike(count)) == [0,1,2]

# notice that the state of the iterator is being encoded manually in the state
#   of the instance itself

# consider that a function in Python creates a stack frame object
from inspect import currentframe, stack
def foo():
	print currentframe() # shows the current stack frame for this function
	print stack() # shows the stack at this stage

# this stack object is an object like any other
# it has members that represent local variables, that represent the code that
#   is being executed, that represent our current execution point
def foo():
	print currentframe().f_lasti # last instruction executed
	print currentframe().f_locals # locals
	print currentframe().f_code # code

# when the function returns, the stack object's references are decremented
#   and it is (probably) garbage collected

# now, the state that our generator like object needs to track
#   could easily be encoded in this frame object
# this leads us into the yield-syntax
def count():
	yield 0
	yield 1
	yield 2

assert hasattr(count(),'__iter__')
assert hasattr(count(),'next')

from collections import Iterator, Iterable
assert isinstance(count(),Iterator)
assert isinstance(count(),Iterable)

# we can conceptualise this syntax as creating an object that is just a
#   function that is not garbage collected until it runs to exhaustion
#   but that can return control at any point

# for example:
from inspect import currentframe
def count():
	print 'first', currentframe().f_lasti
	yield 0
	print 'second', currentframe().f_lasti
	yield 1
	print 'third', currentframe().f_lasti
	yield 2

c = count()
print 'for loop'
for x in c:
	print x

# one thing to take note of is the flow of execution

# we need an instance to capture the state of each particular
#   iteration, which is why all yield-syntax generators
#   must be __call__ed
# that is, the generator definition is akin to a class
#   definition, which we have to instantiate to use

# the first iteration starts at the top of the function and runs until
#   after it yields the first value
# each subsequence iteration runs from the instruction after the previous
#   yield until yielding the next value
# the end of the function raises a StopIteration which is silently 
#   handled by the for-loop

# one interesting thing to note is the difference between the bytecode
#   of a function and a generator
def gen():
	yield
def func():
	return

from dis import dis
dis(gen)
# 210           0 LOAD_CONST               0 (None)
#               3 YIELD_VALUE
#               4 POP_TOP
#               5 LOAD_CONST               0 (None)
#               8 RETURN_VALUE
dis(func)
# 212           0 LOAD_CONST               0 (None)
#               3 RETURN_VALUE

# a generator is actually identical in bytecode to a function
#   with the addition of yielding a value (which returns control and a value
#   to the calling function without cleaning up the stackframe)
# note that yield-syntax generators are able to return, but they are not
#   allowed to return non-None values (* this restriction has been
#   lifted in Python3 to accomodate `yield from` syntax)

def count():
	value = yield 1
	print 'yielded value:', value

for x in count():
	print x
	print 'loop end'

# note that the print statement in the above generator is created
#  when attempting to retrieve the next() value in the SECOND iteration
#  of the loop

c = count()
print next(c)
try: 
	print 'try begin'
	print next(c)
except StopIteration:
	pass
else:
	assert False, 'should have raised the StopIteration'

# to send in a non-None value, we can use the .send() method on the generator

# SYNTAX // GENERATOR METHODS: .send(), .throw(), .close()

# a generator created via yield-syntax comes with this and two other methods:
#   .send() to retrieve the next value and send a value into the generator
#   .throw() to raise an exception at the point of execution
#   .close() to raise a GeneratorExit exception to allow clean-up

# these methods are not part of the fundamental Python object data model, and
#   they are specific to generator objects created via the yield syntax

def latch(value):
	while True:
		v = (yield value)
		if v is not None:
			value = v

x = latch('first')
print '1', next(x)
print '2', next(x)
print '3', x.send('second') 
print '4', next(x)
print '5', next(x)
print '6', next(x)

# SYNTAX // PUMPING A GENERATOR

# note that because the first pass through the generator executes
#   instructions up to the yielding of first value
#   there is no way to capture any information in this pass
# therefore, the first send() call must send a None value
# sending a non-None value will raise a TypeError

# calling next() immediately after creating a generator instance in order
#   to set it up to receive values is often called 'pumping' or 'priming' it

try:
	x = latch(10)
	x.send(20)
except TypeError as e:
	print e
else:
	assert False, 'should have raised the TypeError'

# of course, we can get around this wart with a nice decorator:
def pump(gen):
	def pumped(*args, **kwargs):
		g = gen(*args, **kwargs)
		next(g)
		return g
	return pumped

@pump
def latch(value):
	while True:
		value = (yield value) or value

x = latch(10)
print next(x)
print next(x)
print next(x)
print x.send(20)
print next(x)
print next(x)
print next(x)

# SYNTAX // GENERATOR EXPRESSIONS

# generator expression is just a simpler version of yield-syntax
#   which lacks the .send()/.throw()/.close() methods
#   and which is an instance of the generator in itself

gen = (y for y in [1,2,3])

from collections import Iterable
assert isinstance(gen,Iterable)
for x in gen:
	print x

# note that a generator expression can be iterated over only once
#   as it is an instance of a generator rather than a definition of
#   a generator

# in yield-syntax, code is executed only as we iterate over the generator

# however, note that in a generator expression, the iterated over expression
#   is evaluated at definition time:
def foo():
	print 'foo'
	return [1,2,3]

gen = (y for y in foo())

# SYNTAX // GENERATORS ARE DELAYED/LAZY COMPUTATIONS

# so iterator objects like generators are able to model delayed computations
# in that we can structure the computation to run only as results are required:

from time import sleep
def slow_func():
	x = 1 
	sleep(.05)
	y = 2
	sleep(.05)
	z = 3
	sleep(.05)
	return (x,y,z)

def slow_gen():
	yield 1
	sleep(.05)
	yield 2
	sleep(.05)
	yield 3
	sleep(.05)

# in the former example, we do all processing up front and then return
#   the complete value
# in the latter, we return values as desired ("lazily")

# note that in the case that we need to consume the entire
#   computation before continuing, this doesn't gain us much:
assert list(slow_func()) == list(slow_gen())

# SYNTAX // EXAMPLES: Project Euler #1

# however, let's consider the following problem from Project Euler

# this is an extremely synthetic (contrived) example
 
# Problem 1
# 05 October 2001
# If we list all the natural numbers below 10 that are multiples of 3 or 5, we
#   get 3, 5, 6 and 9. The sum of these multiples is 23.
# Find the sum of all the multiples of 3 or 5 below 1000.

def euler1():
	total = 0
	for x in xrange(1,1001):
		if x%3 == 1 or x%5 == 0:
			total += x
	return total

# note that we have muddied our solution with the need to manually track some
#   state in the form of the total variable

# also, consider what we could parameterise here: the upper bound, the
#   multiples

def euler1a(upper_bound=1001, multiples=(3,5)):
	total = 0
	for x in xrange(1,upper_bound):
		if any(not x%y for y in multiples):
			total += x
	return total

# note that one interesting thing I've done in the above is replace
#   x%y == 0 with not x%y

# this may seem silly, and it is, indeed, incredibly silly
# but consider that `%` means modulo, and modulo
#   has meaningful semantics for anything that is divisible: e.g.,
#   polynomials can be divided, and the remainder of division of
#   some polynomial objects might might be represented as a polynomial object
#   where it's value is not comparable to the integer 0 but may represent
#   the 0-value for that space. here, it might be easiest to just rely on 
#   considering this value in logical terms of being True- or False-equivalent
#   (i.e., the remainder value is True-equivalent if it exists and is not the
#   0-value for this calculation structure)

# but what if we wanted to find the sum of all numbers in the fibonacci
#   sequence that are multiples of 3 or 5? (an admittedly synthetic example)

def euler1b(seq, multiples=(3,5)):
	total = 0
	for x in seq:
		if any(not x%y for y in multiples):
			total += x
	return total

# we're also losing some information by summing all of these values together
# if we wanted to find the max or the min, we would have to write new functions!
		
def euler1c(seq=xrange(1,1001), multiples=(3,5)):
	total = []
	for x in seq:
		if any(not x%y for y in multiples):
			total.append(x)
	return total

assert sum(euler1c()) == 234168

# but do we necessarily need to wait until we've calculated all the values
#   before actually doing something with them?
# what if, for example, we just want the FIRST value that is a multiple
#   of 3 or 5 in our sequence

# need to wrap with iter(), because euler1c() returns a list
#   which is Iterable but not an Iterator (see above for distinction!)
assert next(iter(euler1c())) == 3

# here's where we can use a generator

def euler1d(seq=xrange(1,1001), multiples=(3,5)):
	for x in seq:                           # for each value in seq
		if any(not x%y for y in multiples): # yield it if it's a multiple of
			yield x                         #   any of the multiples

# note how our function has suddenly slimmed down! we no longer
#   explicitly track any state (this state is implicitly tracked for us
#   via the stack frame)
# notice how each line of our function now relates to the problem we're
#   trying to solve, and note how it should be much more readable now
# also, notice how much more flexible our solution has become
#   we don't care about what the sequence provided is

assert next(euler1d()) == 3
assert min(euler1d()) == 3
assert max(euler1d()) == 1000
assert sum(euler1d()) == 234168

# note that when we discussed the generator protocol, we did not
#   state that a generator is a Sized object: i.e., is an object
#   with a __len__ method that can determine it's own size

try:
	len(euler1d())
except TypeError as e:
	print e
else: 
	assert False, 'should have raised the TypeError'

# ASIDE // LENGTH OF AN ABSTRACT ITERATOR

# so, as an aside, how do we calculate the length of a generator?

xs, ys = list(euler1d()), euler1d()
assert len(xs) == sum(1 for _ in ys)

# unfortunately, while this technique works, it means we cannot
#   determine the length of a generator without losing all of its elements
#   or without calculating all of its elements!

# this tells us one important thing: generators are one way; generators are 
#   "exhaustible"

# ASIDE // AVERAGE AND VARIANCE OF AN ABSTRACT ITERATOR 

# another aside, how do we calculate the average of a generator
#   without iterating it over twice?
xs, ys = list(euler1d()), euler1d()
assert len(xs) == sum(1 for _ in ys)

xs, ys = list(euler1d()), euler1d()
assert sum(xs)/len(xs) == \
       (lambda sum, len: sum/len)(
         *reduce(
           lambda *ts: tuple(sum(t) for t in zip(*ts)),
           ((y,1) for y in ys)))

# or, cuter:
xs, ys = list(euler1d()), euler1d()
assert sum(xs)/len(xs) == (lambda x: x.real/x.imag)(sum(y+1j for y in ys))

# this is gratuitous:
# what about the variance?
# variance = average of (x-u)^2 = average of x - average of x^2
xs, ys = list(euler1d()), euler1d()
mean = lambda xs: sum(xs)/len(xs)
assert abs(sum((x-mean(xs))**2 for x in xs)/len(xs) - 
		   (lambda a,b,c: a/c - (b/c)**2)(
             *reduce(
               lambda *ts: tuple(sum(t) for t in zip(*ts)),
               ((y**2,y,1) for y in ys)))) < 0.1 # need to check with tolerance

# SYNTAX // EXAMPLE: Fibonnaci sequence

# let's look at another simple example, the aforementioned fibonacci series

# a formulation using a function might look like this:
def fib(upper_bound):
	rv = [0,1]
	while rv[-1] + rv[-2] < upper_bound:
		rv.append( rv[-1] + rv[-2] )
	return rv

assert fib(10) == [0, 1, 1, 2, 3, 5, 8]
	
# notice that this formulation is actually quite nice to read
# the rv.append( ... ) line encodes our recurrence relationship very clearly

# note that there are some limitations to the above:
# first, we cannot easily rewrite the above to take either an upper bound
#   or take a number of elements; in fact, restricting the returned values
#   from fib is a detail we have no control over and also a detail
#   unrelated to the problem we're trying to solve
# additionally, we have to compute every value of fib() before we can use
#   any of the values and our solution will require memory on the order
#   of the number of values returned, even if we don't need that much memory
#   e.g., if we do sum(fib(10)), we don't need to know about more
#   than a single value at a time!

def fib(a=0, b=1):
	while True:
		yield a
		a, b = b, a+b

# get the first ten elements by slicing
from itertools import islice
assert list(islice(fib(),10)) == [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]

# get the elements under 10
from itertools import takewhile
assert list(takewhile(lambda x: x < 10, fib())) == [0, 1, 1, 2, 3, 5, 8]

# note that fib() is also an infinite generator
# it will continue to yield values forever (and instances will never get
#   garbage collected until they are totally dereferenced or 
#   they are explicitly told to .close())
# we can think of some other problems that naturally lend themslevs
#   to this kind of structure 

# note that these generators also remove a constraint:
#   by merely yielding values back to the caller, they no longer
#   have to specify the returned structure: values can be yielded
#   back and the caller can decide to put them in a list, a set, a
#   ring buffer, &c.

# SYNTAX // EXAMPLE: prime fountain

# for example, a simple prime fountain (using a very inefficient algorithm)
# (note that this is not a sieve algorithm)
from itertools import count
def primes():
	primes = set()
	for x in count(2):
		if all(x%p for p in primes):
			yield x
			primes.add(x)

from itertools import islice
print list(islice(primes(),None,10))

# C EXAMPLE:
#   nwise.c

# the C example shows us an interesting detail
# say we have some instrumentation with a nice C-API that throws samples
#   at us one at a time
# we can easily wrap this API in less than 200 lines of code
#   and expose them to Python

# INTRO TO ITERTOOLS:
#   itertools_intro.py (missing: itertools.chain)

# FURTHER EXAMPLES:
#   {buffered,unbuffered}.py
#   greedy.py
#   {treeify,find,to_ranges}.py

# STREAM PROCESSING

# the exhaustibility of a generator is part of their fundamental denotational
#   semantics 
# that is, a callable that takes a generator as an argument must specify
#   whether it exhausts (partially or fully) by observing any calculations
# if that function touches the generator (by asking for any value) a stateful
#   change has been made, the reprecussions of which may be unobservable
#   in other areas where the generator is referenced
# as a consequence, generators are generally best used as either infinite
#   sequences with an explicit statefulness (e.g., as a coroutine) 
#   or as units of calculation in a pipeline where the foremost
#   input is wholly consumed by the calculation
# so we should think of this as a tool that can be useful for structuring
#   series of computations in series
# since we have easy interoperability with C, we can, for example,
#   take a process that spits out a data via a C API

# OPTIMISATIONS & PERFORMANCE

# there's a consideration of optimisation and performance when
#   we talk about these structures
# there is an indisputable performance benefit to the use of generators
#   in the asymptotic sense: generators can encode a problem with
#   the same time-complexity but better space-complexity (often O(n) to O(1))
# one might also see microbenchmarks talking about how simple operations
#   are faster since the code is executed from "within C"
# these may seem dubious, and I personally believe that they tend to be
#   fairly dubious

# however, structuring a computation as a sequence of generators
#   opens us up to a few interesting optimisation possibilities
# generally, generators are opaque units, like functions

func1 = func2 = func3 = lambda x: list(x)
gen1 = gen2 = gen3 = lambda xs: (x for x in xs)

input_data = (x for x in xrange(10))
output_data = func1(func2(func3(input_data)))

input_data = (x for x in xrange(10))
output_data = gen1(gen2(gen3(input_data)))

from itertools import tee
input_data = tee((x for x in xrange(10)),2)
assert func1(func2(func3(input_data[0]))) == \
  list( gen1( gen2( gen3(input_data[1]))) )

# in the first example, each function has no ability to look into
#   any of the other functions or perform and specialisations as a result
# each unit is totally opaque
# in the latter example, this is true, except because the computations are
#   delayed, each subsequent unit has slightly more information:
#   it can operate on partial results
# therefore, we could create an optimisation as follows:
from itertools import islice
class partialdict(dict):
	def __missing__(self, key):
		return self[frozenset(islice(iter(key),1,None))]
class gentype(object):
	dispatch = partialdict({frozenset(): lambda gen,arg: (gen(arg),'')})
	def __init__(self, gentype):
		self.gentype = gentype
	def __call__(self, gen):
		return typed(gen, gentype=self.gentype)
class typed(object):
	def __init__(self, gen, gentype):
		self.gen, self.gentype = gen, gentype
	def __call__(self, arg):
		if isinstance(arg, wrapped) or isinstance(arg,typed):
			arg_gentype = arg.gentype
		else:
			arg_gentype = ''
		dispatch = gentype.dispatch[frozenset([self.gentype, arg_gentype])]
		rv, rv_type = dispatch(self.gen, arg)
		if not isinstance(rv, wrapped) or rv.gentype != rv_type:
			rv = wrapped(rv, rv_type)
		return rv 
class wrapped(object):
	def __init__(self, gen, gentype):
		self.gen, self.gentype = gen, gentype
	def __iter__(self):
		return self
	def __next__(self):
		return next(self.gen)
	next = __next__
	def send(self, *args, **kwargs):
		return self.gen.send(*args, **kwargs)
	def throw(self, *args, **kwargs):
		return self.gen.throw(*args, **kwargs)
	def close(self, *args, **kwargs):
		return self.gen.close(*args, **kwargs)

passthrough = gentype('passthrough')
gentype.dispatch[frozenset([passthrough.gentype, passthrough.gentype])] = \
  lambda gen,arg: (arg, passthrough.gentype)
gentype.dispatch[frozenset([passthrough.gentype])] = \
  lambda gen,arg: (arg, passthrough.gentype)

@passthrough
def f(xs):
	print 'fff'
	for x in xs:
		yield x

@passthrough
def g(xs):
	print 'ggg'
	for x in xs:
		yield x

def h(xs):
	print 'hhh'
	for x in xs:
		yield x

# result = f(x for x in xrange(10))
# result = f(g(x for x in xrange(10)))
result = f(g(h(x for x in xrange(10))))
print result
print list(result)

# PERFORMANCE // C++ vs Python
#   performance/bythrees.c
#   performance/bythrees.py

# FUNDAMENTAL INTERFACE // PRIMACY OF __iter__&__call__

# say we have a function of the form:
def append_one(xs):
	xs.append(1)

# we have no ability to control the type of the input parameter, xs 
try: append_one([])
except AttributeError as e: print e
else: assert True, 'should NOT have seen AttributeError'

try: append_one({})
except AttributeError as e: print e
else: assert False, 'should have seen AttributeError'

try: append_one(set())
except AttributeError as e: print e
else: assert False, 'should have seen AttributeError'

try: append_one(tuple())
except AttributeError as e: print e
else: assert False, 'should have seen AttributeError'

# we cannot control these types statically
# we can do it dynamically, but this is mostly meaningless
def append_one(xs):
	assert hasattr(xs,'append')
	xs.append(1)
# all we've done is trade an AttributeError for an AssertionError!

# because we cannot control the types statically, it seems to me
#   that we should instead attempt to minimise our exposure to these kinds of
#   errors
# notice that the only typing we have available is a form of structural
#   typing, where we type on the presence of certain, specially named methods
# we have no insight into the methods themselves: they are totally opaque
#   so we do not have and will never have the ability to type on or 
#   control the implementation of these parameters
# that is, .append() might exist, but it could do anything 

# we can minimise these kinds of errors by limiting ourselves to certain,
#   established interface,s and it appears that the two, prime interfaces
#   in Python are __iter__ and __call__

def append_one(updater):
	updater(1)

append_one([].append)
append_one(lambda x,y=(): y + (x,) )
append_one(set().add)
append_one(lambda x,y={}: y.update({x:x}))

# __call__ is a fundamental interface that is available to:
#   generators
#   functions (and C-functions)
#   type objects
#   class objects
#   instance objects (via tp_call/__call__/())

# another fundamental interface is __iter__
# this is the interface available to: 
#   generators
#   all collection types in Python (set(), {}, [], (), '')
#   it is the interface used by the `for` construct

# if we encode the complexity of our problems in such a way
#   that the only required interfaces are __call__ and __iter__
#   we open ourselves up to an enormously flexible mode

# FUNDAMENTAL INTERFACE // COMPLEXITY PATHWAYS
# ???

# FUNDAMENTAL INTERFACE // Example: greedy{_simple,}.py

# HARD PROBLEM

# we looked at an example of calculating the variance of a generator
#   and noticed that, in order to stay within a constant memory usage
#   constraint, we would need to collect all values within a single pass
# what if we had a basic function that we did NOT want to exhaust some 
#   provided Iterable
# this problem looks simple, but it is, in fact, extremely difficult
#   to solve completely, as the deeper you try to solve it, the 
#   more you have to touch (or hack around)

# we just want to peek one value ahead without changing xs
def peek(xs):
	return next(xs)

# however, each time we peek, xs is advanced
xs = (x for x in xrange(1,100) if not x%3)
assert peek(xs) == 3 and peek(xs) <> 3

# we know that we can tee an Iterable to copy it if we want to be able to
#   traverse it twice

xs = (x for x in xrange(1,100) if not x%3)
from itertools import tee
xs1, xs2 = tee(xs,2)
assert peek(xs1) == 3 and peek(xs2) == 3

# however, because a generator is an opaque structure, this means that
#   we can never control the internal state of the generator
#   once we try to "observe" a value (i.e., force a calculation to yield
#   the next value)
# as a consequence, tee() acts merely as a buffer and the original
#   iterable is no longer usable
# the original iterable will be mutated by iteration through the tee()
#   proxies to it, and these proxies will handle buffering the values
#   yielded
# as a result, we CANNOT rewrite peek as follows:

def peek(xs):
	xs,_ = tee(xs,2)
	return next(xs)

xs = (x for x in xrange(1,100) if not x%3)
assert peek(xs) == 3  and peek(xs) <> 3 # still doesn't work!

# additionally, from within the scope of the function,
#   there's no way we can "reach out" to tell the caller to make
#   a buffering copy
# the only thing we can do is force the caller to explicitly
#   handle the buffering copy via tee() before calling out function

# this means that exhaustion is part of the denotational semantics
#   of Python functions that accept iterables
# the function must specify whether it iterates through or exhausts its
#   parameters so the caller can know whether or not they need to 
#   make buffering copies

# the only trick around this is as follows:
def swaparg(pos, argspec):
	def parse(args, kwargs):
		if isinstance(pos,basestring) and pos in kwargs:
			source, pos_ = kwargs, pos
		elif isinstance(pos,basestring):
			source, pos_ = args, argspec.args.index(pos)
		elif argspec.args[pos] in kwargs:
			source, pos_ = kwargs, argspec.args[pos]
		else:
			source, pos_ = args, pos
		return source, pos_
	def find(args, kwargs):
		source, pos = parse(args, kwargs)
		return source[pos]
	def replace(args, kwargs, value):
		source, pos = parse(args, kwargs)
		source[pos] = value
		return args, kwargs
	return find, replace

from itertools import chain
from inspect import stack, getargspec
def copied_iterable(pos):
	def decorator(func):
		argspec = getargspec(func)
		find, replace = swaparg(pos, argspec)
		def wrapper(*args, **kwargs):
			it = find(args, kwargs)
			caller_copy, local_copy = tee(it,2)

			# replace in callers
			caller_frames = (frame[0] for frame in stack()[1:])
			caller_locals = (frame.f_locals for frame in caller_frames)
			replacements = (((ls,k) for k,v in ls.iteritems() if v is it)
			                 for ls in caller_locals)
			for ls,k in chain.from_iterable(replacements):
				ls[k] = caller_copy

			# replace locally
			args, kwargs = replace(list(args), kwargs.copy(), local_copy)

			return func(*args, **kwargs)
		return wrapper
	return decorator

@copied_iterable('xs')
def peek(xs):
	return next(xs)

xs = (x for x in xrange(1,100) if not x%3)
assert peek(xs) == 3 and peek(xs) == 3 # works!
assert peek(xs=xs) == 3 and peek(xs=xs) == 3 # works!

# this illustrates an issue with Python decorators
#   we lose (and have no way to reconstruct) the original
#   argspec of the original function
# therefore, the following will fail!

# @copied_iterable('xs')
# @copied_iterable('ys')
# def peek(xs,ys):
# 	return next(xs), next(ys)

# xs = (x for x in xrange(1,100) if not x%3)
# ys = (y for y in xrange(1,100) if not y%5)
# assert peek(xs,ys) == (3,5) and peek(xs,ys) == (3,5) # works!

# functions are opaque, in that we aren't guaranteed to be able to
#   inspect and control them as above, so the above technique might fail if
#   some functions higher in the stack frame are not Python functions
# additionally, let's consider that somewhere in the caller of peek,
#   we could have sent the value of the iterable we want to copy
#   to some generator
# the generator's frames won't show up in the stack frames of 
#   peek(), so we also need to go in and search through every
#   generator to make sure that it doesn't have an old reference
#   to the old iterable
# generators are opaque in that we can't really inspect or control
#   them from the outside except via the interface next/send/throw/close
# therefore, even if we can find all the generators that might have
#   captured references to the iterable, we might be unable to alter them
