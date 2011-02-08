import unittest

import math
from gpyconf import Configuration
from gpyconf.fields import IntegerField, CharField, FloatField, NumberField
from gpyconf.fields.base import Field

class ConfigurationSuperclass(Configuration):
    field1_from_superclass = IntegerField()

class ConfigurationSuperclass2(ConfigurationSuperclass):
    field1_from_superclass2 = CharField()

class InheritedConfiguration(ConfigurationSuperclass2):
    field1_from_subclass = FloatField()


class InheritanceTest(unittest.TestCase):
    def test_configuration_inheritance(self):
        self.config = InheritedConfiguration()
        self.assert_('field1_from_superclass' in self.config.fields)
        self.assert_('field1_from_superclass2' in self.config.fields)
        self.assert_('field1_from_subclass' in self.config.fields)

        self.config.field1_from_superclass = 42
        self.config.field1_from_superclass2 = 'hello world'
        self.config.field1_from_subclass = round(math.pi, 10)

        self.config.save()
        del self.config

        self.config = InheritedConfiguration()
        self.assertEqual(self.config.field1_from_superclass, 42)
        self.assertEqual(self.config.field1_from_superclass2, 'hello world')
        self.assertEqual(self.config.field1_from_subclass, round(math.pi, 10))

    def test_field_inheritance(self):
        self.assertTrue(Field.abstract)
        class SubField(Field):
            pass
        self.assertFalse(SubField.abstract)
        self.assertTrue(NumberField.abstract)
        self.assertFalse(IntegerField.abstract)
        self.assertFalse(FloatField.abstract)

if __name__ == '__main__':
    unittest.main()
