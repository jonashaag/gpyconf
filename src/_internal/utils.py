# %FILEHEADER%
# Contains various utilities used within gpyconf.

class NONE:
    def __repr__(self):
        return 'NONE'

class DEFAULT:
    def __repr__(self):
        return 'DEFAULT'

def isiterable(iterable, include_strings=False):
    if isinstance(iterable, str):
        return include_strings
    try:
        iter(iterable)
    except TypeError:
        return False
    else:
        return True

def create_empty_file(file):
    open(file, 'w').close()

def escape_filename(name, return_escaped_char=False):
    e = ['/', '\\']
    if '\\' in name:
        # windows
        e.reverse()
    if return_escaped_char:
        return e[0]
    return name.replace(*e)

def filename_from_classname(klass, ext=''):
    import re
    import types

    if isinstance(klass, str):
        name = klass
    elif isinstance(klass, types.ClassType):
        name = klass.__name__
    else:
        name = klass.__class__.__name__

    filename = re.sub('([a-z])([A-Z])', '\g<1>_\g<2>', name).lower()
    if ext:
        return filename+'.'+ext
    else:
        return filename


class RGBTuple(tuple):
    """ Tuple for RGB values """
    @classmethod
    def from_hexstring(cls, value):
        """ Returns a RGB tuple from hexstring ('#RRGGBB') """
        if value.startswith('#'):
            value = value[1:]
        return cls(int(value[i:i+2], 16) for i in (0, 2, 4))

    def to_string(self):
        """ Returns the hexstring representation ('#RRGGBB') of ``self``"""
        def _exp(v):
            return v if len(v) == 2 else '0'+v
        return '#' + ''.join(map(lambda x:_exp(hex(x)[2:]).upper(), self))

    def __str__(self):
        return self.to_string()

    def __xmlserialize__(self):
        return tuple(self)
