# coding: utf-8
# %FILEHEADER%

"""
    Contains gpyconf's default shipped fields.
"""

from .base import Field
from .._internal.exceptions import InvalidOptionError
from .._internal.utils import RGBTuple
from .._internal.dicts import ordereddict
from .mutable import *


class BooleanField(Field):
    """ A field representing the :class:`bool` datatype """
    allowed_types = 'boolean compatibles (True, False, 1, 0)'
    default = False

    def to_python(self, value):
        try:
            return bool(int(value))
        except ValueError:
            if value == 'True':
                return True
            elif value == 'False':
                return False
            else:
                self.validation_error(value)

    def python_to_conf(self, value):
        return unicode(int(value))

    def conf_to_python(self, value):
        return bool(int(value))


class MultiOptionField(Field):
    """
    A (typically dropdown) selection field.

    Takes an extra argument ``options`` which is a tuple of two-tuples (or any
    other iterable datatype in this form) where the first item of the two-tuple
    holds a value and the second item the label for entry.

    The value item might be of any type, the label item has to be a string.

    .. note::
       If your backend runs in compatibility mode, values may only be
       instances of any type convertable from string to that type using
       ``thattype(somestring)`` (for example, :class:`int`, :class:`float`
       support that type of conversion). Otherwise, reading values from the
       backend will fail.

    Example::

        ... = MultiOptionField('My options', options=(
            ('foo', 'Select me for foo'),
            ('bar', 'Select me for bar'),
            (42, 'Select me for the answer to Life, the Universe, and Everything')
        ))
    """
    # TODO: Rewrite this Field and make it use real dictionaries.
    def custom_default(self):
        return self.values[0]

    def allowed_types(self):
        return 'unicode-strings in %s' % self.values

    def on_initialized(self, sender, kwargs):
        self.options = ordereddict()
        self.values = []
        options = kwargs.pop('options')
        for value, text in options:
            self.options[text] = value # 'This is a foo option' : 'foo'
            self.values.append(value)

    def to_python(self, value):
        if value not in self.values:
            self.validation_error(value)
        return value

    def conf_to_python(self, value):
        def _find_value():
            for _value in self.values:
                if str(_value) == value:
                    return _value
        _value = _find_value()
        if _value is None:
            self.validation_error(value)
        return type(_value)(value)

    def python_to_conf(self, value):
        if type(value)(str(value)) != value:
            raise InvalidOptionError(self,
                "%r has an incompatible type (%r)" % (value, type(value)))
        return str(value)


class NumberField(Field):
    """
    A field representing the :class:`int` datatype. Takes three extra
    arguments:

    :param min:
        The minimal value allowed, defaults to 0.
    :param max:
        The maxmimal value allowed, defaults to 100.
    """
    _abstract = True
    min = 0
    max = 100

    def custom_default(self):
        return self.min

    def on_initialized(self, sender, kwargs):
        for key in ('min', 'max'):
            if key in kwargs:
                setattr(self, key, kwargs.pop(key))

    def python_to_conf(self, value):
        return unicode(value)

    def conf_to_python(self, value):
        return self.num_type(value)

    def to_python(self, value):
        try:
            return self.num_type(value)
        except (TypeError, ValueError):
            self.validation_error(value)

    def __valid__(self):
        return not (self.min > self.value or self.value > self.max)

class IntegerField(NumberField):
    num_type = int

class FloatField(IntegerField):
    num_type = float


class CharField(Field):
    """ A simple on-line-input field """
    allowed_types = 'unicode-strings'
    default = ''
    blank = True

    def __blank__(self):
        return self.value == ''

    def to_python(self, value):
        return unicode(value)

class PasswordField(CharField):
    """
    A simple password field. Saves values as a base64 encoded unicode-string.
    """

    def python_to_conf(self, value):
        # we want at least some basic password covering
        return value.encode('base64')

    def conf_to_python(self, value):
        from binascii import Error as BinError
        try:
            return (value+'\n').decode('base64')
        except BinError:
            self.validation_error(value)
            # which will be catched by get_value

class IPAddressField(CharField):
    """ An IP address field with simple validation """
    def __valid__(self):
        ip = self.value
        if ip.count('.') != 3 and ip.count('.') != 5 or \
        not ip.replace('.', '').isdigit():
            return False
        # very, very basic ip syntax testing
        # TODO: ipv6! :-D
        else:
            parts = [int(part) for part in ip.split('.')]
            for part in parts:
                if not (0 <= part <= 255):
                    # not in ip range
                    return False
        return True


class URIField(CharField):
    """
    Field for any type :abbr:`URIs (Uniform Resource Identifier)`.

    An URI follows the following scheme::
        scheme://scheme specific part
    """
    _scheme = '[a-z][a-z\.\-:\d]*://.*'
    allowed_types = "unicode strings following the URI scheme (%r)" % _scheme

    def __valid__(self):
        from re import match
        return match(self._scheme, self.value)

class URLField(CharField):
    """
    Field for any type of :abbr:`URLs (Uniform Resource Locator)` and base
    class for :class:`FileField`. The :attr:`value` of this field is an
    instance of :class:`urlparse.ParseResult` and follows common URL syntax.

    :class:`urlparse.ParseResult` or :class:`unicode` may be used to update
    this field's value.
    """
    allowed_types = 'unicode-strings and urlparse.ParseResults'

    def custom_default(self):
        from urlparse import urlparse
        return urlparse('')

    def to_python(self, value):
        from urlparse import urlparse, urlunparse, ParseResult
        if isinstance(value, ParseResult):
            return value
        if isinstance(value, tuple):
            # unparse pure tuples so they can be parsed into a ParseResult tuple
            value = urlunparse(value)
        return urlparse(value)

    def python_to_conf(self, value):
        from urlparse import urlunparse
        return urlunparse(value)

class FileField(URLField):
    """
    Field for file selection. Usage is similar to that of the :class:`URLField`.

    When updating the value, strings without a scheme
    (something like ``http://`` or ``file://``) are handled as if they had
    the ``file://`` scheme.
    """
    def custom_default(self):
        from urlparse import urlparse
        return urlparse('file:///')

    def to_python(self, value):
        uri = URLField.to_python(self, value)
        if not uri.scheme:
            uri = URLField.to_python(self, 'file://'+value)
        return uri


class EmailAddressField(CharField):
    """ A field for email addresses """
    allowed_types = 'unicode-strings following the email address scheme'

class TextField(CharField):
    """ A field for (multi-line) text input """
    pass


class DateTimeField(Field):
    """ A field for date/time input """
    allowed_types = 'datetime.datetime instances'

    def custom_default(self):
        from datetime import datetime
        return datetime.utcnow().replace(microsecond=0)

    def python_to_conf(self, value):
        # convert to timestamp
        import time
        return unicode(time.mktime(value.timetuple()))

    def conf_to_python(self, value):
        from datetime import datetime
        return datetime.fromtimestamp(float(value))

    def to_python(self, value):
        return value.replace(microsecond=0)
        # we throw away the microsecond thing - it's irrelevant
        # and causes problems with conversion using `time.mktime`

    def __valid__(self):
        from datetime import datetime
        return isinstance(self.value, datetime)


class ColorField(Field):
    """ A field for color selections """
    _changed_signal = 'color-set'
    allowed_types = 'hexadecimal color strings (#RRGGBB) or ' \
                    'a tuple of integers (r, g, b)'
    default = RGBTuple((0, 0, 0))

    def to_python(self, value):
        if isinstance(value, basestring):
            return RGBTuple.from_hexstring(value)
        else:
            return RGBTuple(value)

    def python_to_conf(self, value):
        return value.to_string()


class FontField(DictField):
    """
    A field for font selections.

    The field's value is a :class:``dict`` following this layout::

        {
            'name' : 'The font name (e.g. Sans)',
            'size' : 'The font size in pixels (e.g. 10)',
            'bold' : True or False,
            'italic' : True or False,
            'underlined' : True or False
            'color' : 'The font color (e.g. #CC00FF, case insensitive)',
        }

    Every field of this dict except for the `name` and `size` keys may be
    empty, the `color` key then defaults to `#000000` (black) and the
    `bold` and `italic` and `underlined` default to :const:`False`
    """
    def custom_default(self):
        return {'name' : 'Sans', 'size' : 10, 'color' : '#000000',
                'italic' : False, 'bold' : False, 'underlined' : False}

    def on_initialized(self, sender, kwargs):
        kwargs.update({
            'merge_default' : True,
            'keys' : 'fromdefault'
        })
        DictField.on_initialized(self, sender, kwargs)


__all__ = tuple(name for name, object in locals().iteritems()
                if isinstance(object, type) and issubclass(object, Field))
