#!/usr/bin/env python

from itertools import tee, izip
def pairwise( iterable, n ):
	iterables = tee( iterable, n )      # create n copies of the iterable
	for i,it in enumerate(iterables):   # for the nth copy of the iterable
		for _ in xrange( i ):           #   advance it n values
			next( it )                  # e.g., the 0th iterable advanced 0
			                            #       the 1st iterable advances 1
	return izip( *iterables )           # take these staggered iterables
	                                    #   and zip them together
	                                    # i.e., return tuples of the first
	                                    #   elements from each, the second
	                                    #   elements from each, &c.

# this generator yields contiguous 
#   subsets of a given iterable
def contiguous( iterable ):
	buffer = []                         # start with an empty buffer
	for x,y in pairwise( iterable, 2 ): # look at the elements pairwise
		buffer.append( x )              # put the element into the buffer
		if (y-x) > 1:                   # if the next element is a jump
			yield buffer                #   yield the buffer and reset
			buffer = []
	yield buffer + [y]                  # yield whatever is left over

def to_ranges( iterable ):
	for subset in contiguous( iterable ):
		yield '%d' % subset[0] \
		       if len(subset) == 1 else \
		       '%d-%d' % (subset[0], subset[-1])

if __name__ == '__main__':
	assert list(contiguous([1,2,3,5,10,11,12,17])) == \
	         [[1,2,3],[5],[10,11,12],[17]]
	assert list(to_ranges([1,2,3,5,10,11,12,17])) == \
	         ['1-3','5','10-12','17']

