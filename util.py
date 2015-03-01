import random

def random_characters(r):
    pool = [chr(ord('A') + x) for x in range(26)] + [str(x) for x in range(10)]
    n = len(pool)
    indices = sorted(random.sample(xrange(n), r))
    return "".join(pool[i] for i in indices)

def get_mime_type(ext):
    pass
