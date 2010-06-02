# coding: utf-8
# %FILEHEADER%

# A backend dumping values to pure-python-code
import __builtin__
from .filebased import FileBasedBackend
from . import NONE, MissingOption
from pprint import pformat, isreadable

MAX_LINE_LENGTH = 80

class SpecialHandlers(object):
    @staticmethod
    def datetime(string):
        return 'import datetime', string

    @staticmethod
    def RGBTuple(string):
        return False, string


class PythonModuleBackend(FileBasedBackend):
    initial_file_content = '__all__ = ()'

    def __init__(self, backref, filename=None):
        FileBasedBackend.__init__(self, backref, 'py', filename)
        self.module = PythonModule(self.file)

    def read(self):
        self.module = PythonModule.from_module(__import__(self.file.rstrip('.py')))

    def save(self):
        print self.file
        with open(self.file, 'w') as fobj:
            fobj.write(self.module.to_code())

    def set_option(self, name, value):
        if not isreadable(value):
            raise TypeError("The option '%s' (current value: '%s') can't be "
                            "dumped" % (name, value))

        self.module.attributes[name] = value

        if name in __builtin__.__dict__:
            self.emit('log', "The option '%s' overwrites the builtin of the "
                             "same name" % name, level='warning')

    def get_option(self, name, default=NONE):
        try:
            return self.module.attributes[name]
        except KeyError:
            if default is not NONE:
                return default
            else:
                raise MissingOption(name)

    def reset_all(self):
        raise NotImplementedError()

    @property
    def options(self):
        return self.module.attributes.keys()


class PythonModule(object):
    def __init__(self, filename, attributes=None):
        if not filename.endswith('.py'):
            filename += '.py'
        self.filename = filename
        if attributes is None:
            attributes = {}
        self.attributes = attributes

    @staticmethod
    def find_import(type_):
        return 'from %s import %s' % (type_.__module__, type_.__name__)

    def to_code(self):
        """
        Return a string containing valid python code to be written
        into the resulting python module.
        """
        imports = set()
        attributes = {}

        for attribute, value in self.attributes.iteritems():
            _import = None
            value_string = pformat(value)
            typename = type(value).__name__

            if value is not None and typename not in __builtin__.__dict__:
                _import = self.find_import(type(value))
            try:
                res = getattr(SpecialHandlers, typename.replace('.', '_'))
            except AttributeError:
                pass
            else:
                _import, value_string = res(value_string)
            attributes[attribute] = value_string
            if _import:
                imports.add(_import)

        return '\n\n'.join(x for x in (
            ('\n'.join(imports)),
            ('__all__ = ' + pformat(tuple((attributes.keys())))),
            '\n'.join('%s = %s' % (a, v) for a, v in attributes.iteritems())
            ) if x)


    def save(self):
        with open(self.filename, 'w') as fobj:
            fobj.write(self.to_code())

    @classmethod
    def from_module(cls, module, *kwargs):
        """
        Create a new :class:`PythonModule` with all attributes gained from
        ``module``.
        """
        module_dict = dict(((k, getattr(module, k)) for k in module.__all__
                            if not k.startswith('_')))
        return cls(module.__file__, attributes=module_dict, *kwargs)

