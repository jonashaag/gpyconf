# coding: utf-8
# Tests various aspects of the gpyconf.fields.MultiOptionField.

# NOTE:
# If there's one error and you're using the ConfigParser backend,
# everything's alright (string-based backends can't store lists)

from itertools import izip
import gpyconf
import gpyconftest
from datetime import datetime
import unittest

OPTIONS1 = {
    'Some label with ünicode' : 'string',
    'asdasd' : 43,
    'foo' : datetime.now(),
    'bar' : range(5)
}

OPTIONS2 = (
    (12.1, 'hi'),
    (12.2, 'there'),
    ([1,2,3], 'foo') # fails
)

class MultiOptionFieldTestConf(gpyconftest.Configuration):
    a = gpyconf.fields.MultiOptionField(options=izip(OPTIONS1.values(), OPTIONS1.keys()))
    b = gpyconf.fields.MultiOptionField(options=OPTIONS2)


class MultiOptionFieldTestCase(unittest.TestCase):
    def setUp(self):
        self.conf = MultiOptionFieldTestConf()

    def runTest(self):
        stored = {}
        for _field in ('a', 'b'):
            field = self.conf.fields[_field]
            for value in field.values:
                field.value = value
                self.assert_(field.value == value == getattr(self.conf, _field))
                stored[_field] = value

        self.conf.save()
        del self.conf
        self.setUp()

        for _field in ('a', 'b'):
            field = self.conf.fields[_field]
            self.assertEqual(getattr(self.conf, _field), stored[_field])

if __name__ == '__main__':
    unittest.main()
