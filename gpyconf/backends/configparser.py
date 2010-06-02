# %FILEHEADER%

from ConfigParser import SafeConfigParser, NoOptionError
from .filebased import FileBasedBackend
from . import NONE, MissingOption

class ConfigParserBackend(FileBasedBackend):
    """
    Wrapper class for :class:`ConfigParser.ConfigParser`.
    This is the default backend.
    """
    section = 'default_section'
    compatibility_mode = True

    def __init__(self, backref):
        FileBasedBackend.__init__(self, backref, 'ini')
        self.parser = SafeConfigParser()
        if not self.parser.has_section(self.section):
            self.parser.add_section(self.section)
        self.read()

    def read(self):
        with open(self.file) as fobj:
            self.parser.readfp(fobj)

    def save(self):
        with open(self.file, 'wb') as fobj:
            self.parser.write(fobj)

    def set_option(self, name, value):
        try:
            self.parser.set(self.section, name, value)
        except TypeError, e:
            if "option values must be strings" in e:
                raise TypeError("Option values must be strings, not %s" \
                                                % type(value).__name__)
            else:
                raise TypeError(e)

    def get_option(self, name, default=NONE):
        try:
            return self.parser.get(self.section, name)
        except NoOptionError:
            if default is not NONE:
                return default
            else:
                raise MissingOption(name)

    @property
    def options(self):
        return self.parser.options(self.section)

    def reset_all(self):
        FileBasedBackend.reset_all(self)
