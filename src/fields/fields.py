# coding: utf-8
# %FILEHEADER%

# Contains gpyconf's default fields shipped.

from .base import NoConfigurationField, Field
from .._internal.exceptions import InvalidOptionError
from .._internal.utils import isiterable, RGBTuple
from .._internal.dicts import ordereddict

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


class ListField(Field):
    # TODO: Docs
    def custom_default(self):
        return list()

    def on_initialized(self, sender, kwargs):
        self.length = kwargs.pop('length', None)
        self.item_type = kwargs.pop('item_type', None)

    def allowed_types(self):
        s = 'lists/tuples or any other iterable'
        if self.length is not None:
            s += ' of length %d' % self.length
        if self.item_type is not None:
            s += " that items are a '%s'" % self.item_type
        return s

    def to_python(self, iterable):
        return list(iterable)

    def python_to_conf(self, value):
        from .._internal.serializers import serialize_list
        return serialize_list(value)

    def conf_to_python (self, value):
        from .._internal.serializers import unserialize_list
        return unserialize_list(value, self.item_type)

    def __valid__(self):
        if self.length is not None and self.length != len(self.value):
            return False
        if self.item_type is not None:
            return all(map(lambda x:isinstance(x, self.item_type), self.value))
        return True


class DictField(Field):
    # TODO: Docs
    def custom_default(self):
        return dict()

    def on_initialized(self, sender, kwargs):
        self.keys = kwargs.pop('keys', None)
        self.merge_default = kwargs.pop('merge_default', True)

        if self.keys is not None:
            if self.keys == 'fromdefault':
                self._keys_setfromdefault()

        self.statically_typed = isinstance(self.keys, dict)

    def _keys_setfromdefault(self):
        self.keys = dict((k, type(v)) for k, v in self.default.iteritems())

    def type_of(self, key):
        if not self.statically_typed:
            raise TypeError("Can't get type of '%s' key of non-static typed %s"
                            % (key, self.name))
        return self.keys[key]

    def allowed_types(self):
        if self.keys is None:
            return 'dicts/dict-like objects'
        else:
            return 'dicts/dict-like objects with keys %s' % self.keys

    def to_python(self, value):
        to_dict = lambda x:x if isinstance(x, dict) else dict(x)
        try:
            if not self.merge_default:
                return to_dict(value)
            else:
                return dict(self.default, **to_dict(value))
        except TypeError:
            self.validation_error(value)

    def conf_to_python(self, value):
        from .._internal.serializers import unserialize_dict

        if not self.statically_typed:
            self.emit('log', "No static key types given, unserialized values "
                             "will all be of type 'unicode'", level='warning')
        return unserialize_dict(value, self.keys)

    def python_to_conf(self, value):
        from .._internal.serializers import serialize_dict
        return serialize_dict(value)

    def __valid__(self):
        if not self.keys: return True # no validation, so always True

        if set(self.keys) != set(self.value): return False # different keys
        if not self.statically_typed: return True

        for k, v in self.value.iteritems():
            if not isinstance(v, self.keys[k]):
                return False
        return True


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
                "'%s' has an incompatible type ('%s')" % (value, type(value)))
        return str(value)


class IntegerField(Field):
    """
    A field representing the :class:`int` datatype. Takes three extra
    arguments:

    :param min:
        The minimal value allowed, defaults to 0.
    :param max:
        The maxmimal value allowed, defaults to 100.
    :param step:
        The incrementation step, defaults to 1.
    :param decimals:
        The number of decimals to be stored and displayed, defaults to 0
        (no decimals places).
    """
    allowed_types = 'ints and floats'
    _default_values = {
        'max' : 100,
        'min' : 0,
        'decimals' : 0,
        'step' : 1
    }

    def custom_default(self):
        return self.min

    def on_initialized(self, sender, kwargs):
        for key, default in self._default_values.iteritems():
            setattr(self, key, kwargs.pop(key, default))

    def python_to_conf(self, value):
        return unicode(value)

    def conf_to_python(self, value):
        return float(value)

    def to_python(self, value):
        if not isinstance(value, float):
            try:
                value = float(value)
            except (TypeError, ValueError):
                self.validation_error(value)
        return int(value) if value.is_integer() else value

    def __valid__(self):
        value = self.value
        return not (self.min > value or value > self.max or value % self.step)

    def validation_error(self, faulty=None):
        if not isinstance(faulty, (int, float)):
            faulty = type(faulty).__name__
        raise InvalidOptionError(self,
            "IntegerField allows only int or float types between %d and %d, "
            "stepped with %d, not %s" % (self.min, self.max, self.step, faulty))


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
    A simple password field. Saves values as base64 encoded unicode-string.
    """

    def python_to_conf(self, value):
        return value.encode('base64')
        # we want at least some basic password covering

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
    allowed_types = "unicode strings following the URI scheme ('%s')" % _scheme

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
        from urlparse import urlparse, ParseResult
        if isinstance(value, ParseResult):
            return value
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
        # TODO: cleanup.
        if isiterable(value):
            return RGBTuple(value)
        return RGBTuple.from_hexstring(value)

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
    _default = {'name' : 'Sans', 'size' : 10, 'color' : '#000000',
                'italic' : False, 'bold' : False, 'underlined' : False}

    def on_initialized(self, sender, kwargs):
        kwargs.update({
            'merge_default' : True,
            'keys' : 'fromdefault'
        })
        DictField.on_initialized(self, sender, kwargs)


__all__ = tuple(name for name, object in locals().iteritems()
                if isinstance(object, type) and issubclass(object, Field))
