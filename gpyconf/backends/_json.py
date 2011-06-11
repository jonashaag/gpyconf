# %FILEHEADER%
"""
The json backend docstring
"""
from .filebased import FileBasedBackend
from . import NONE, MissingOption
try:
    import json
except ImportError:
    import simplejson as json


class JSONBackend(FileBasedBackend):
    """
    Backend based on `JSON <http://json.org>`_ files
    """
    initial_file_content = '{}'

    def __init__(self, backref):
        FileBasedBackend.__init__(self, backref, extension='json')

    def read(self):
        with open(self.file) as fobj:
            self.json_tree = json.load(fobj) or {}

    def save(self):
        with open(self.file, 'w') as fobj:
            json.dump(self.tree, fobj, indent=4)

    def set_option(self, name, value):
        self.json_tree[name] = value

    def get_option(self, name, default=NONE):
        try:
            return self.json_tree[self.section][name]
        except KeyError:
            if default is not NONE:
                return default
            else:
                raise MissingOption(name)

    @property
    def tree(self):
        return self.json_tree

    @property
    def options(self):
        return self.json_tree.keys()
