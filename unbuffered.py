#!/usr/bin/env python

def pairs(source):
	while True:
		x, y = next(source), next(source)
		yield (x,y)

if __name__ == '__main__':
	from sys import stdin
	from itertools import count, takewhile

	input_stream = (x.rstrip() for x in
	                takewhile(bool,
	                  (stdin.readline() for _ in count())))

	for p in pairs(input_stream):
		print 'two values', ', '.join(p)
