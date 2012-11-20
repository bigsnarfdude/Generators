#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
from __future__ import division

def greedy(target, source):
	source = iter(source)
	total = 0
	while True:
		x = next(source)
		while (total+x) <= target:
			total += x
			yield x

if __name__ == '__main__':
	from random import randint
	amount = randint(0,1000)
	coins = [1,5,10,25,100,500,1000,2000]
	print '{:.2f} in coins is: {}'.format(amount/100,
	        ', '.join('{:.2f}'.format(x/100) for x in
	        greedy(amount,reversed(coins))))
