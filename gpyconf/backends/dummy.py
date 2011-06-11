# %FILEHEADER%

from __future__ import print_function
from . import Backend
from . import NONE, MissingOption

_print = print
def print(*args, **kwargs):
    return _print(*(["DummyBackend:"]+list(args)), **kwargs)

class DummyBackend(Backend):
    """
    A dummy backend. Does not store any values; :meth:`get_option` returns the
    corresponding field's current value instead of a stored one.

    Useful for debugging and playing around with gpyconf.
    """
    def read(self):
        print("Read")

    def save(self):
        print("Save")

    def set_option(self, name, value):
        print("Set option %s to %s" % (name, value))

    def get_option(self, name, default=NONE):
        print ("Get option %s" % name)
        try:
            return self.backref().fields[name].value
        except KeyError:
            print("Option not set, using default value %s" % default)
            if default:
                return default
            else:
                raise MissingOption

    def reset_all(self):
        print ("Reset all")

    @property
    def options(self):
        return self.backref().fields.keys()
