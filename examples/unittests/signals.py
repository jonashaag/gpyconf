# Tests wether signal communication works.

import unittest

class StorageTestCase(unittest.TestCase):
    def setUp(self):
        from all_fields import AllFieldsTest
        self.conf = AllFieldsTest()
        self.conf.connect('field-value-changed', self.field_value_changed_cb)

    def field_value_changed_cb(self, sender, field_name, new_value):
        self.assertEqual(self.conf.fields[field_name].value, new_value)

    def runTest(self):
        self.conf.run_frontend()


if __name__ == '__main__':
    unittest.main()
