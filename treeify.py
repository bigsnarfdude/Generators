#!/usr/bin/env python

def pairwise( iterable, n=2 ):
	from itertools import tee, izip, islice
	return izip(*(islice(it,pos,None) for pos,it in enumerate(tee(iterable, n))))
def prepend( *values ):
	from itertools import chain
	return chain( values[:-1], values[-1] )
def unpackargs( func ):
	return lambda args: func(*args)

if __name__ == '__main__':
	from sys import stdin, argv
	dirsep = argv[1] if len(argv) == 2 else '/'

	from itertools import tee, count, takewhile, izip, imap
	from operator import eq
	input = takewhile(lambda x:any(map(bool,x)),(map(str.rstrip,stdin.readline().split(dirsep)) for _ in count()))

	depth = lambda vals: len(list(takewhile(bool,list(vals))))
	zipwith = lambda f, x: (lambda x,y: izip(f(x),y))(*tee(x,2))

	for depth, line in zipwith(lambda x: imap(depth, prepend([False],(map(unpackargs(eq),izip(*pair)) for pair in pairwise(x)))),input):
		print ' '.join(' ' * len(x) for x in line[:depth]) + (dirsep if depth else '') + dirsep.join(x for x in line[depth:]) 
