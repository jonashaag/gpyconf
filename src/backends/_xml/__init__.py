# %FILEHEADER%

from ..filebased import FileBasedBackend
from .. import NONE, MissingOption

from xmlserialize import serialize_to_file, unserialize_file
from lxml.etree import XMLSyntaxError

class XMLBackend(dict, FileBasedBackend):
    ROOT_ELEMENT = 'configuration'
    initial_file_content = '<{0}></{0}>'.format(ROOT_ELEMENT)

    def __init__(self, backref, extension='xml', filename=None):
        dict.__init__(self)
        FileBasedBackend.__init__(self, backref, extension, filename)

    def read(self):
        try:
            return unserialize_file(self.file)
        except XMLSyntaxError, err:
            self.log('Could not parse XML configuration file: %s' % err,
                     level='error')

    def save(self):
        serialize_to_file(self, self.file, root_tag=self.ROOT_ELEMENT)

    def get_option(self, item):
        try:
            return self.__getitem__(item)
        except KeyError:
            raise MissingOption(item)
    set_option = dict.__setitem__

    options = property(lambda self:self.keys())
    tree = property(lambda self:self)

    def reset_all(self):
        self._create_file()
        self.clear()
