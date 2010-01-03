# Tests wether signal communication works.

import unittest

class StorageTestCase(unittest.TestCase):
    def setUp(self):
        import sys, os
        sys.path.append(os.path.abspath(os.path.join(
                        os.path.dirname(__file__), os.pardir)))

        from all_fields import AllFieldsTest
        self.conf = AllFieldsTest()
        self.conf.connect('field-value-changed', self.field_value_changed_cb)

    def field_value_changed_cb(self, sender, field, new_value):
        self.assertEqual(field.value, new_value)
        self.assertEqual(getattr(self.conf, field.field_var), new_value)

    def runTest(self):
        self.conf.run_frontend()


if __name__ == '__main__':
    unittest.main()
