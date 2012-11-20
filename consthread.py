# consthread.py

import Queue, threading
from genqueue import genfrom_queue

class ConsumerThread(threading.Thread):
    def __init__(self,target):
         threading.Thread.__init__(self)
         self.setDaemon(True)
         self.in_q   = Queue.Queue()
         self.target = target
    def send(self,item):
         self.in_q.put(item)
    def run(self):
        self.target(genfrom_queue(self.in_q))

# Example use
if __name__ == '__main__':
    from follow import *
    from apachelog import *
    from broadcast import *

    def find_404(log):
        for r in (r for r in log if r['status'] == 404):
            print r['status'],r['datetime'],r['request']

    def bytes_transferred(log):
        total = 0
        for r in log:
            total += r['bytes']
            print "Total bytes", total

    c1 = ConsumerThread(find_404)
    c1.start()
    c2 = ConsumerThread(bytes_transferred)
    c2.start()

    lines = follow(open("run/foo/access-log"))  # Follow a log
    log   = apache_log(lines)           # Turn into records
    broadcast(log,[c1,c2])         # Broadcast to consumers
