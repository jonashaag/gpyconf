# coding: utf-8
# %FILEHEADER%

# gpyconf's logging system.

from __future__ import print_function
import os
from operator import itemgetter
from textwrap import wrap as wordwrap

# debug levels
LEVELS = (
    (0, 'INFO'),
    (1, 'DEBUG'),
    (2, 'WARNING'),
    (3, 'ERROR'),
)

DEFAULT_LOGFILE = os.path.expanduser('~/.%(classname)s_gypconf.log')
DEFAULT_FORMAT = 'gpyconf::%(level)s: %(message)s'
DEFAULT_VERBOSE_FORMAT = 'gpyconf(%%(classname)s)%s' % DEFAULT_FORMAT[7:]

class DefaultFormatter(object):
    """ A default debug string formatter """
    _ljust_to = max([len(s) for i, s in LEVELS])+2

    def __init__(self, verbose=False):
        self.verbose = verbose

    def format(self, level, message, classname=None, field=None):
        _message = ':'.join((level[1],)).ljust(self._ljust_to)

        if classname is not None and self.verbose:
            _message += '(%s)' % classname
        if field is not None:
            _message += "%s '%s': " % (field._class_name, field.field_var)

        message = ('\n'+' '*self._ljust_to).join(wordwrap(message, 79-self._ljust_to))
        return _message + message + '\n'


class Logger(object):
    def __init__(self, classname, level=None, verbose=False,
        formatter=DefaultFormatter, use_file=False, file=None, use_stdout=True):

        self.level = level if level is not None else LEVELS[2]
        self.classname = classname
        self.file = file if file is not None else \
                    DEFAULT_LOGFILE % {'classname' : classname}

        self.formatter = formatter(verbose=verbose)

        self.use_file = use_file
        self.use_stdout = use_stdout
        if not (use_file or use_stdout):
            raise TypeError('No logging output specified. Use at least one of '
                'stdout or file output')

    @property
    def level(self):
        return self._level

    @level.setter
    def level(self, level):
        if level in LEVELS:
            self._level = level
            # level given as tuple of (index, name)
        else:
            try:
                self._level = LEVELS[level]
                # level given as index
            except (TypeError, IndexError):
                level_names = map(itemgetter(1), LEVELS)
                try:
                    self._level = LEVELS[level_names.index(level.upper())]
                except (ValueError, AttributeError):
                    raise TypeError("Invalid `level` parameter given")

    def _print(self, *args, **kwargs):
        if self.use_stdout:
            print(*args, **kwargs)
        if self.use_file:
            print(file=self.file, *args, **kwargs)

    def info(self, *args, **kwargs):
        self.log(level=LEVELS[0], *args, **kwargs)

    def debug(self, *args, **kwargs):
        self.log(level=LEVELS[1], *args, **kwargs)

    def warning(self, *args, **kwargs):
        self.log(level=LEVELS[2], *args, **kwargs)

    def error(self, *args, **kwargs):
        self.log(level=LEVELS[3], *args, **kwargs)

    def log(self, message, level=None, field=None):
        if level is None:
            raise TypeError('Buuh!')
        if level[0] < self.level[0]:
            # lower level, throw the message away
            return
        self._print(self.formatter.format(level, message, field=field,
                                          classname=self.classname))
