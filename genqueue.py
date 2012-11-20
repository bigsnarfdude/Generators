# genqueue.py
#
# Generate a sequence of items that put onto a queue

def sendto_queue(source,thequeue):
    for item in source:
        thequeue.put(item)
    thequeue.put(StopIteration)

def genfrom_queue(thequeue):
    while True:
        item = thequeue.get()
        if item is StopIteration: break
        yield item

# Example
if __name__ == '__main__':

    # A consumer.   Prints out 404 records.
    def print_r404(log_q):
        log = genfrom_queue(log_q)
        r404 = (r for r in log if r['status'] == 404)
        for r in r404:
            print r['host'],r['datetime'],r['request']

    import Queue, threading
    from follow import *
    from apachelog import *

    log_q = Queue.Queue()
    log_thr = threading.Thread(target=print_r404,
                               args=(log_q,))
    log_thr.setDaemon(True)
    log_thr.start()

    # Feed the consumer thread
    lines = follow(open("run/foo/access-log"))
    log   = apache_log(lines)
    sendto_queue(log,log_q)

