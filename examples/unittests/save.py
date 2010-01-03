# Tests wether saving and reading configuration works correctly.
import unittest

class StorageTestCase(unittest.TestCase):
    def setUp(self):
        import sys, os
        sys.path.append(os.path.abspath(os.path.join(
                        os.path.dirname(__file__), os.pardir)))

        from all_fields import AllFieldsTest
        self._class = AllFieldsTest
        self.options = {}

    def runTest(self):
        ins = self._class()
        for var, field in ins.fields.iteritems():
            self.options[var] = field.value

        ins.save()
        del ins

        ins = self._class()

        for var in self.options:
            self.assertEqual(self.options[var], getattr(ins, var))


if __name__ == '__main__':
    unittest.main()
