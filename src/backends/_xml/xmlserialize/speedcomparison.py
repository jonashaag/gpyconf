import time
import xmlserialize
from test import TESTCASES

import pickle as pickel

def timeit(callable, args=(), kwargs=dict(), loops=100):
    start_time = time.time()
    for _ in xrange(loops):
        callable(*args, **kwargs)
    duration = time.time() - start_time
    return duration, duration/loops

if __name__ == '__main__':
    print "Running tests with xmlserialize..."
    xtime = timeit(lambda: xmlserialize.unserialize_string(
                            xmlserialize.serialize(TESTCASES)))
    print "TOTAL DURATION: %rs | AVERAGE CALL DURATION: %rs" % xtime

    print "Running tests with pickel..."
    ptime = timeit(lambda: pickel.loads(pickel.dumps(TESTCASES)))
    print "TOTAL DURATION: %rs | AVERAGE CALL DURATION: %rs" % ptime

    x, p = xtime[0], ptime[0]
    print "Pickel is %d times %s than xmlserialize" % (
            max(x, p)/min(x, p), ('faster', 'slower')[x < p])
