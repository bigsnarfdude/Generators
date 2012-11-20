#!/usr/bin/env python

def sieve( n ):
	from array import array
	S_m = array( 'L', (i     if i!=1 else 0 for i in xrange(0,n+1)) ) 
	S_p = array( 'L', ((i-1) if i!=0 else 0 for i in xrange(0,n+1)) )
	S_n = array( 'L', ((i+1) if i!=n else n for i in xrange(0,n+1)) )
	def iterate( p ):
		while p < n:
			yield p
			p = S_n[p]
	from itertools import takewhile
	for p in iterate(2):
		for m, p, n in [(m,S_p[m],S_n[m]) for m in takewhile(lambda x: x<=n, (p*f for f in iterate(p)))]:
			S_m[m], S_n[p], S_p[n] = 0, n, p
	return (m for m in S_m if m)

if __name__ == '__main__':
	from itertools import islice
	print islice(sieve(10000),0,10)
