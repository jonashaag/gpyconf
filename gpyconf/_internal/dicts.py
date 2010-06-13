# Contains various dictionary-derivated datastructures.

from UserDict import DictMixin
from collections import defaultdict

try:
    from collections import OrderedDict as ordereddict
except ImportError:
    class ordereddict(dict, DictMixin):
        def __init__(self, iterable=None, **kwiterable):
            try:
                self.__end
            except AttributeError:
                self.clear()
            self.update(iterable, **kwiterable)

        def clear(self):
            self.__end = end = []
            end += [None, end, end]     # sentinel node for doubly linked list
            self.__map = {}             # key --> [key, prev, next]
            dict.clear(self)

        def __setitem__(self, key, value):
            if key not in self:
                end = self.__end
                curr = end[1]
                curr[2] = end[1] = self.__map[key] = [key, curr, end]
            dict.__setitem__(self, key, value)

        def __delitem__(self, key):
            dict.__delitem__(self, key)
            key, prev, next = self.__map.pop(key)
            prev[2] = next
            next[1] = prev

        def __iter__(self):
            end = self.__end
            curr = end[2]
            while curr is not end:
                yield curr[0]
                curr = curr[2]

        def __reversed__(self):
            end = self.__end
            curr = end[1]
            while curr is not end:
                yield curr[0]
                curr = curr[1]

        def popitem(self, last=True):
            if not self:
                raise KeyError('dictionary is empty')
            key = reversed(self).next() if last else iter(self).next()
            return key, self.pop(key)

        def __reduce__(self):
            items = [[k, self[k]] for k in self]
            tmp = self.__map, self.__end
            del self.__map, self.__end
            inst_dict = vars(self).copy()
            self.__map, self.__end = tmp
            if inst_dict:
                return (self.__class__, (items,), inst_dict)
            return self.__class__, (items,)

        def keys(self):
            return list(self)

        setdefault = DictMixin.setdefault
        update = DictMixin.update
        pop = DictMixin.pop
        values = DictMixin.values
        items = DictMixin.items
        iterkeys = DictMixin.iterkeys
        itervalues = DictMixin.itervalues
        iteritems = DictMixin.iteritems

        def __repr__(self):
            if not self:
                return '%s()' % (self.__class__.__name__,)
            return '%s(%r)' % (self.__class__.__name__, self.items())

        def copy(self):
            return self.__class__(self)

        @classmethod
        def fromkeys(cls, iterable, value=None):
            return cls((k, value) for k in iterable)

        def __eq__(self, other):
            if isinstance(other, ordereddict):
                return len(self)==len(other) and \
                       all(p==q for p, q in  zip(self.items(), other.items()))
            return dict.__eq__(self, other)

        def __ne__(self, other):
            return not self == other


class ordereddefaultdict(ordereddict, defaultdict):
    def __init__(self, default_factory, *args, **kwargs):
        defaultdict.__init__(self, default_factory)
        ordereddict.__init__(self, *args, **kwargs)


class dotaccessdict(dict):
    def __getattr__(self, attr):
        try:
            return self[attr]
        except KeyError:
            raise AttributeError(attr)


class FieldsDict(ordereddict, dotaccessdict):
    @property
    def name_value_dict(self):
        return dict(((name, field.value) for name, field in self.iteritems()))
