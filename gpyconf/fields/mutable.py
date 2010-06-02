# %FILEHEADER%
from .base import Field

__all__ = ('ListField', 'DictField')

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
            return all(isinstance(item, self.item_type) for item in self.value)
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
            raise TypeError("Can't get type of '%s' key of non-statically typed %s" \
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
