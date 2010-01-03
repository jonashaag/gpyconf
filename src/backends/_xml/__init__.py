# %FILEHEADER%

from ..filebased import FileBasedBackend
from .. import NONE, MissingOption

from xmlserialize import serialize, unserialize

class XMLBackend(dict, FileBasedBackend):
    ROOT_ELEMENT = 'configuration'
    initial_file_content = '<%s></%s>' % (ROOT_ELEMENT, ROOT_ELEMENT)

    def __init__(self, backref, extension='xml', filename=None):
        dict.__init__(self)
        FileBasedBackend.__init__(self, backref, extension, filename)

    def read(self):
        with open(self.file) as fobj:
            self.update(unserialize(fobj))

    def save(self):
        with open(self.file, 'w') as fobj:
            serialize(self, root_node=self.ROOT_ELEMENT, file=fobj)

    def get_option(self, item):
        try:
            return self.__getitem__(item)
        except KeyError:
            raise MissingOption(item)
    set_option = lambda self, item, value: try_(self.__setitem__, item, value)

    options = property(lambda self:self.keys())
    tree = property(lambda self:self)

    def reset_all(self):
        self._create_file()
        self.clear()
