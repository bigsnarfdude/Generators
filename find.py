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

from itertools import imap
def find( s ):
	substrings = imap(lambda x: ''.join(x),pairwise(s,7))
	match = lambda substr: substr[ :3].islower() and \
	                       substr[4: ].islower() and \
	                       substr[3:4].isupper()
	return next( (x for x in substrings if match(x)), None ) # None is the
	                                                         #   default retval

if __name__ == '__main__':
	s = 'jfjheNeKdlwoqjasJjasjDfk'
	#                 ---=---
	assert find(s) == 'jasJjas'

	s = 'jfjheNeKdlwoqjasJjasjDfk'
	#                 ---=---
	assert find(s) == 'jasJjas'
