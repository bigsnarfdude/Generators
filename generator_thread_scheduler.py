def thread_schedule(generators):
    thread_data = defaultdict(list)
    threads = [g() for g in generators()]
    while True:
        try:
            for t in threads:
                data = thread_data[t.__name__]
                consumer, data = t.send(data)
                thread_data[consumer].append(data)
        except StopIteration: break

