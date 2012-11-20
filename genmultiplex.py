# genmultiplex.py

import threading, Queue
from genqueue import *
from gencat import *

def multiplex(sources):
    in_q = Queue.Queue()
    consumers = []
    for s in sources:
        thr = threading.Thread(target=sendto_queue,
                               args=(s,in_q))
        thr.start()
        consumers.append(genfrom_queue(in_q))
    return gen_cat(consumers)

if __name__ == '__main__':
    import follow
    foo_log = follow.follow(open("run/foo/access-log"))
    bar_log = follow.follow(open("run/bar/access-log"))
    for line in multiplex([foo_log,bar_log]):
        print line
    
