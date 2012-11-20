# print_count.py

def print_count(n):
    yield "Hello World\n"
    yield "\n"
    yield "Look at me count to %d\n" % n
    for i in xrange(n):
        yield "   %d\n" % i
    yield "I'm done!\n"

# Example:

if __name__ == '__main__':
    out = print_count(10)
    print "".join(out)

    # Route to a file
    out = print_count(5)
    f = open("count.txt","wb")
    for chunk in out:
        f.write(chunk)
    f.close()

