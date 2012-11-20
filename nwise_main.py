#!/usr/bin/env python

if __name__ == '__main__':
	from sys import stdin
	from nwise import nwise
	print "\n".join(",".join(x) for x in nwise(y.strip() for y in stdin))
