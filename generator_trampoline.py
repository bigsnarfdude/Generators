def coroutine_trampoline(generators, start, init_data):
    CRs = {}
    for g in generators:
        if g is start:
            coroutine = g(init_data)
            curr, data = coroutine.next()
        else:
            coroutine = g(); coroutine.next()
        CRs[coroutine.__name__] = coroutine

    while True:
        try: curr, data = CRs[curr].send(data)
        except StopIteration: break

