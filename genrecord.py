# genrecord.py
import struct

def gen_records(record_format, thefile):
    record_size = struct.calcsize(record_format)
    while True:
          raw_record = thefile.read(record_size)
          if not raw_record:
              break
          yield struct.unpack(record_format, raw_record)

# Example use
if __name__ == '__main__':
    f = open("stockdata.bin","rb")
    for name, shares, price in gen_records("<8sif",f):
        print "%10s %10d %10.2f" % (name.strip('\x00'),shares,price)
