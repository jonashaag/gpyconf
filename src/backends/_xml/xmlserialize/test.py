# encoding: utf-8
from __future__ import print_function
import sys
import operator
import xmlserialize

if '--quiet' in sys.argv:
    print = lambda *a, **k: None

TESTCASES = {
    'BooleanSerializer' : (-1, 0, 1, True, False, u'a'),
    'IntegerSerializer' : (-10*5+1, -1, -0, 0, 1, 10*5+1),
    'FloatSerializer'   : (-10*5-0.007, -0.00000024, -0, 0, 1, 0.00000013),
    'LongSerializer'    : (-10**20, -10**10, -0, 0, 10**10, 10**20),
    #'RangeSerializer'   : (xrange(100), xrange(1, 10), xrange(-10, 10)),
    'StringSerializer'  : (u'Hello', u'World', u'whøt\'s', u'↑?'),
    'NoneTypeSerializer': (None,)
}

TESTCASES['SimpleIterableSerializer'] = tuple(
    typ(TESTCASES.values()) for typ in
                            xmlserialize.SimpleIterableSerializer.serializes)
TESTCASES['KeyValueIterableSerializer'] = TESTCASES.copy()
TESTCASES['SimpleIterableSerializer'] += (TESTCASES['KeyValueIterableSerializer'],)


def assert_equal(*items):
    assert reduce(operator.eq, items), ' != '.join(map(repr, items))

def run_tests(serialize=xmlserialize.serialize,
              unserialize=xmlserialize.unserialize_string, testcases_name='\b'):
    total_errors = 0
    for serializer, testcases in TESTCASES.iteritems():
        print("Running %s testcases for %s..." % (testcases_name, serializer))
        errors = 0
        for index, testcase in enumerate(testcases, 1):
            try:
                assert_equal(
                    testcase,
                    unserialize(serialize(testcase))['object']
                )
            except AssertionError as message:
                print("Testcase #%d failed: %s" % (index, message))
                errors += 1
        if not errors:
            print(' PASSED ----'.rjust(79, '-'))
        else:
            print((' %d ERRORS ----' % errors).rjust(79, '-'))

        total_errors += errors

    print()
    print(("**** TOTAL ERRORS: %d " % total_errors).ljust(79, '*'))
    print()
    print()


def main():
    run_tests()

    def _namespace1():
        from os import remove
        from tempfile import mkstemp
        tempfile = mkstemp()[1]

        def serialize(object):
            with open(tempfile, 'w') as fobj:
                return xmlserialize.serialize_to_file(object, fobj)
        def unserialize(throwaway, *args, **kwargs):
            with open(tempfile, 'r') as fobj:
                return xmlserialize.unserialize_file(fobj, *args, **kwargs)

        run_tests(serialize, unserialize, testcases_name='temporary file save')
    _namespace1()

if __name__ == '__main__':
    for x in xrange(int(sys.argv[sys.argv.index('--n')+1]) if '--n' in sys.argv else 1):
        main()
