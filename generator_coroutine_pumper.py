def coroutine(func):
    def start(*args, **kwargs):
        cr =  func(*args, **kwargs)
        cr.next()
        return cr
    return start

@coroutine
def generator_counter():
    count = 0
    while True:
        c = yield count
        count +=1

