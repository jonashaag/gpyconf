# Tests the gpyconf.fields.FontField, particularly saving.
import unittest
import gpyconf
import gpyconftest

class FontFieldTestConf(gpyconftest.Configuration):
    f = gpyconf.fields.FontField()

class FontFieldTestCase(unittest.TestCase):
    def setUp(self):
        self.conf = FontFieldTestConf()

    def runTest(self):
        value = self.conf.f
        self.conf.save()
        del self.conf
        self.setUp()
        self.assertEqual(value, self.conf.f)

        print "don't change the value!"
        self.conf.run_frontend()
        self.assertEqual(value, self.conf.f)

        print "now change it"
        self.conf.run_frontend()
        self.assertNotEqual(value, self.conf.f)

if __name__ == '__main__':
    unittest.main()
