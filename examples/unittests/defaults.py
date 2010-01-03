# Tests wether all fields handle default values correctly.

import unittest
import gpyconf

class DefaultTestConf(gpyconf.Configuration):
    foo = gpyconf.fields.BooleanField(default=True)
    bar = gpyconf.fields.CharField(default='Hello')
    blubb = gpyconf.fields.FileField(default='file:///home/user/foo')
    peng = gpyconf.fields.IntegerField(default=42, min=11, max=121)
    multi = gpyconf.fields.MultiOptionField(default='foo', options=(
        ('foo', 'Foobar'),
        ('bar', 'Bar')
    ))


class DefaultTest(unittest.TestCase):
    def setUp(self):
        self.conf = DefaultTestConf()

    def runTest(self, new=True):
        from urlparse import urlparse

        for var, default in {
            'foo' : True,
            'bar' : 'Hello',
            'blubb' : urlparse('file:///home/user/foo'),
            'peng' : 42
        }.iteritems():
            self.assertEqual(getattr(self.conf, var), default)

        if new:
            for var, new in {
                'foo' : False,
                'bar' : 'Hi there',
                'blubb' : 'blaaah',
                'peng' : 45
            }.iteritems():
                setattr(self.conf, var, new)
            self.conf.reset()
            self.runTest(new=False)

if __name__ == '__main__':
    unittest.main()
