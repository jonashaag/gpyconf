# Tests if hidden and editable are handled correctly.
import unittest
import gpyconf
import gpyconftest

class HiddenAndEditableTestConf(gpyconftest.Configuration):
    editable = gpyconf.fields.IntegerField(default=42)
    not_editable = gpyconf.fields.IntegerField(default=42, editable=False)

    hidden = gpyconf.fields.IntegerField(default=42, hidden=True)

    logging_level = 'info'


class HiddenAndEditableTestCase(unittest.TestCase):
    def setUp(self):
        self.conf = HiddenAndEditableTestConf()

    def runTest(self):
        self.conf.editable = 43
        # should change
        try:
            self.conf.not_editable = 43
        except AttributeError:
            pass
        else:
            raise RuntimeError("Value set but field is not editable")

        self.assertEqual(self.conf.fields.not_editable.default, self.conf.not_editable)
        # value mustn't have changed

        self.conf.run_frontend()

        self.assertEqual(self.conf.fields.hidden.default, self.conf.hidden)
        # value shouln't have changed (frontend shouldn't show this field)

if __name__ == '__main__':
    unittest.main()
