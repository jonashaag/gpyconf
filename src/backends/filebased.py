# %FILEHEADER%

import os
from .._internal.utils import create_empty_file, filename_from_classname
from . import Backend

class FileBasedBackend(Backend):
    """
    Abstract base class for file based backends
    (backends that use files as storage for configuration options).
    """
    create_new = True
    initial_file_content = ''

    def __init__(self, backref, extension='', filename=None):
        Backend.__init__(self, backref)
        self.file = filename or filename_from_classname(backref(), extension)

        if not os.path.exists(self.file):
            if self.create_new:
                self._create_file()
            else:
                raise IOError("No such file: %s" % self.file)

    def reset_all(self):
        self._create_file()
        self.read()

    def _create_file(self):
        with open(self.file, 'w') as fobj:
            fobj.write(self.initial_file_content)
