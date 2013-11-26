from itertools import islice

def window(seq, n=3):
    "Returns a sliding window (of width n) over data from the iterable"
    it = iter(seq)
    # result = tuple(islice(it, (n+1)//2))
    result = tuple(islice(it, n))
    if len(result) > 0:
        yield result
    for elem in it:
        result = result[1 if len(result)==n else 0:] + (elem,)
        yield result
    # result = result[1:]
    # while len(result) >= (n+1)//2:
    #     yield result
    #     result = result[1:]

print len(list(window(range(12*4), 4)))
print list(window(range(12*4), 4))