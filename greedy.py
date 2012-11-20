#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
from __future__ import division

def pump(gen):
	next(gen)
	return gen.send

def predicate(x, state=0):
	value = yield
	while True:
		if state+value <= x:
			state += value
			value = yield True
		else:
			value = yield False

from itertools import repeat, chain, takewhile
greedy = lambda items, predicate: chain.from_iterable(takewhile(predicate,repeat(x)) for x in reversed(items))

if __name__ == '__main__':
	from itertools import groupby
	from random import randint
	amount = randint(0,1000)
	pred = pump(predicate(amount))

	coins = greedy([1,5,10,25,100,500,1000,2000],pred)
	print 'Your change for {:.2f}$ = {}'.format(
	        amount/100,
	        ' + '.join(
	          '{:d}×{}'.format(
	            sum(1 for _ in cs),
	            ('{:d}¢' if c < 100 else '{:.0f}$').format(c if c < 100 else c/100))
	        for c,cs in groupby(coins)))
	###

	roman = {  1:  'i',   4: 'iv',    5:  'v',   9: 'ix',  10: 'x',
	          40: 'ix',  50:  'x',   90: 'xc', 100:  'c', 400: 'cd',
	         500:  'd', 900: 'cm', 1000:  'm',}

	from random import randint
	year = randint(1900,2200)
	pred = pump(predicate(year))

	numerals = greedy(sorted(roman),pred)
	print 'The year {} is written {}'.format(
			 year,
	         ''.join(roman[x].upper() for x in list(numerals)))

