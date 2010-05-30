import unittest
import gpyconf.fields
import gpyconf._internal.exceptions
from gpyconftest import Configuration


class TestMutableFields(unittest.TestCase):
    def test_listfield(self):
        class Config1(Configuration):
            field = gpyconf.fields.ListField()

        conf = Config1()
        self.assertEqual(conf.field, [])

        list1 = [1, 2, 3, 4, 99, 'a', 'b', 'c']
        conf.field = list1

        conf.save()
        del conf
        conf = Config1()
        self.assertEqual(conf.field, map(unicode, list1))
        # everything should be unicode after serialization and deserialization

    def test_typed_listfield(self):
        class Config2(Configuration):
            field = gpyconf.fields.ListField(item_type=float)

        conf = Config2()
        list1 = [1.2, 1.3, 42.42, 1.00000978, 3e-300]
        conf.field = list1

        conf.save()
        del conf
        conf = Config2()
        self.assertEqual(conf.field, list1)

        conf.field = ['a', 'b', 'c']
        self.assertRaises(gpyconf._internal.exceptions.InvalidOptionError,
                          conf.save)

    def test_fixed_length_listfield(self):
        class Config3(Configuration):
            field = gpyconf.fields.ListField(length=7)

        conf = Config3()

        conf.field = []
        self.assert_(not conf.fields.field.isvalid())

        conf.field = [1, 2, 3]
        self.assert_(not conf.fields.field.isvalid())

        conf.field = range(7)
        self.assert_(conf.fields.field.isvalid())

    def test_typed_and_fixed_length_listfield(self):
        class Config4(Configuration):
            field = gpyconf.fields.ListField(item_type=int, length=3)

        conf = Config4()

        conf.field = [1, 2]
        self.assert_(not conf.fields.field.isvalid())

        conf.field = [1, 2, 3.000]
        self.assert_(not conf.fields.field.isvalid())

        conf.field = range(3)
        self.assert_(conf.fields.field.isvalid())

        conf.save()
        del conf
        conf = Config4()

        self.assert_(all(isinstance(item, int) for item in conf.field))


if __name__ == '__main__':
    unittest.main()
