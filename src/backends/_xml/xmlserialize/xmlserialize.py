#
#     Copyright (c) 2009 Jonas Haag <jonas@lophus.org>.
#     All rights reserved.
#     License: 2-clause-BSD (Berkley Software Distribution) license
#
#     http://github.com/jonashaag/xmlserialize.py
#
# The full text of the 2-clause BSD license follows.
#
# The 2-clause Berkley Software Distribution license
# ==================================================
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

__all__ = (
    'NoSuchSerializer', 'NoSuchUnserializer', 'Serializer',
    'GenericTypeSerializer', 'SimpleTypeSerializer', 'IntegerSerializer',
    'FloatSerializer', 'LongSerializer', 'BooleanSerializer', 'StringSerializer',
    'SimpleIterableSerializer', 'KeyValueIterableSerializer', 'RangeSerializer',
    'serialize_atomic', 'serialize_to_file', 'unserialize_atomic', 'unserialize_file',
    'unserialize_string'
)

from lxml.etree import ElementTree, Element, _ElementTree
from lxml.etree import fromstring as elementtree_fromstring, tostring as elementtree_tostring


def memoized_function(function, cache={}):
    def cached_function(*args, **kwargs):
        _kwargs = tuple(kwargs.iteritems())
        try:
            cache_key = hash((id(function), args, _kwargs))
        except TypeError:
            try:
                import cPickle as pickel
            except ImportError:
                import pickle as pickel
            cache_key = pickel.dumps((id(function), args, _kwargs))
        if cache_key not in cache:
            cache[cache_key] = function(*args, **kwargs)
        return cache[cache_key]
    return cached_function

@memoized_function
def try_import(module, names=('__name__',)):
    try:
        module = __import__(module, fromlist=names)
    except ImportError:
        return

    for name in names:
        if not hasattr(module, name):
            return
    return module

from sys import version_info
HAVE_PYTHON3 = version_info[0] > 2
if not HAVE_PYTHON3:
    def try_decode(s):
        try:
            return s.decode('utf-8')
        except UnicodeDecodeError as unicode_decode_error:
            try:
                import chardet
            except ImportError:
                raise unicode_decode_error
            else:
                encoding = chardet.detect(s)['encoding']
                if encoding is not None:
                    return s.decode(encoding)
                else:
                    raise UnicodeDecodeError(s)


class NoSuchSerializer(Exception):
    def __init__(self, object):
        Exception.__init__(self,
            "No serializer for type '%s' found"  % type(object))

class NoSuchUnserializer(Exception):
    def __init__(self, type_):
        Exception.__init__(self,
            "No (un)serializer for type '%s' found" % type_)

class PleaseUseUnicode(Exception):
    def __init__(self):
        Exception.__init__(self,
            "Can't serialize object of type 'str' -- please use unicode!")

class _SerializerMeta(type):
    def __new__(cls, name, bases, dct):
        for method_name in ('unserialize', 'serialize'):
            if method_name in dct:
                dct[method_name] = classmethod(dct[method_name])

        serializes = dct.setdefault('serializes', NotImplemented)
        if serializes is not NotImplemented:
            if not isinstance(serializes, (list, tuple)):
                dct['serializes'] = (serializes,)

        return type.__new__(cls, name, bases, dct)

class Serializer(object):
    __metaclass__ = _SerializerMeta
    serializes = NotImplemented
    promote_lazy = False

    def serialize(cls, object, tag_name, serialize_as):
        raise NotImplementedError()

    def unserialize(cls, xml_element, unserialize_to):
        raise NotImplementedError()

    @classmethod
    def subclasses(cls):
        return get_subclasses(cls, recursive=True)

    @classmethod
    def get_for_type(cls, type_):
        if isinstance(type_, Serializer):
            return type_

        for subclass in cls.subclasses():
            if subclass.serializes is NotImplemented: continue
            for serializes in subclass.serializes:
                if serializes is type_ or serializes.__name__ == type_:
                    return serializes, subclass
        raise NoSuchUnserializer(type_ if isinstance(type_, str)
                                       else type_.__name__)



class GenericTypeSerializer(Serializer):
    serializes = () # object
    promote_lazy = True

class NoneTypeSerializer(Serializer):
    serializes = type(None)

    def serialize(cls, object, tag_name, serialize_as):
        return Element(tag_name, type='NoneType')

    def unserialize(cls, xml_element, unserialize_to):
        return None

class SimpleTypeSerializer(Serializer):
    def unserialize(cls, xml_element, unserialize_to):
        return unserialize_to(xml_element.text)

    def serialize(cls, object, tag_name, serialize_as):
        element = Element(tag_name, type=serialize_as.__name__)
        element.text = unicode(object)
        return element


class IntegerSerializer(SimpleTypeSerializer):
    serializes = int

class FloatSerializer(SimpleTypeSerializer):
    serializes = float

class LongSerializer(SimpleTypeSerializer):
    serializes = long

class BooleanSerializer(SimpleTypeSerializer):
    serializes = bool
    unserialize_map = {
        True  : ('True',  'true', 1, '1'),
        False : ('False', 'false', 0, '0')
    }

    def unserialize(cls, xml_element, unserialize_to):
        if xml_element.text in cls.unserialize_map[True]:
            return True
        elif xml_element.text in cls.unserialize_map[False]:
            return False
        else:
            return bool(xml_element.text)

class StringSerializer(SimpleTypeSerializer):
    serializes = (unicode, str)

    def serialize(cls, object, tag_name, serialize_as):
        if not HAVE_PYTHON3 and serialize_as is str:
            try:
                object = try_decode(object)
            except UnicodeDecodeError:
                raise PleaseUseUnicode()
        return super(cls, cls).serialize(unicode(object), tag_name, str)

    def unserialize(cls, xml_element, unserialize_to):
        return unicode(xml_element.text)


import datetime
import time
class DateTimeSerializer(Serializer):
    serializes = datetime.datetime

    def serialize(cls, object, tag_name, serialize_as):
        element = Element(tag_name, type=serialize_as.__name__)
        element.text = str(time.mktime(object.timetuple()))
        return element

    def unserialize(cls, xml_element, unserialize_to):
        return datetime.datetime.fromtimestamp(float(xml_element.text))


class SimpleIterableSerializer(Serializer):
    serializes = (tuple, list, set, frozenset)
    item_key = 'item'

    def serialize(cls, object, tag_name, serialize_as):
        container_element = Element(tag_name, type=serialize_as.__name__)
        for item in object:
            container_element.append(serialize_atomic(item, cls.item_key))
        return container_element

    def unserialize(cls, xml_element, unserialize_to):
        container = list()
        for child in xml_element.getchildren():
            container.append(unserialize_atomic(child))
        return unserialize_to(container)

class KeyValueIterableSerializer(Serializer):
    serializes = dict
    if try_import('collections', 'OrderedDict'):
        serializes += (__import__('collections').OrderedDict,)
    if try_import('collections', 'defaultdict'):
        serializes += (__import__('collections').defaultdict,)

    def serialize(cls, object, tag_name, serialize_as):
        container_element = Element(tag_name, type=serialize_as.__name__)
        for key, value in object.iteritems():
            container_element.append(serialize_atomic(value, key))
        return container_element

    def unserialize(cls, xml_element, unserialize_to):
        return cls.unserialize_tree(xml_element.getchildren(), unserialize_to)

    @classmethod
    def unserialize_tree(cls, xml_tree, unserialize_to, *args, **kwargs):
        container = unserialize_to()
        for child in xml_tree:
            object = unserialize_atomic(child, *args, **kwargs)
            container[child.tag] = object
        return container

class RangeSerializer(Serializer):
    sep = ' to '
    # TODO: step
    serializes = xrange

    def serialize(cls, range, tag_name, serialize_as):
        element = Element(tag_name, type=serialize_as.__name__)
        element.text = '%s%s%s' % (range[0], cls.sep, range[-1]+1)
        return element

    def unserialize(cls, xml_element, unserialize_to):
        return unserialize_to(*map(int, xml_element.text.split(cls.sep)))

@memoized_function
def get_subclasses(klass, recursive=False, max_depth=None, current_depth=0):
    subclasses = []
    for subclass in klass.__subclasses__():
        if subclass is not object:
            subclasses.append(subclass)

        if recursive:
            for subclass in get_subclasses(subclass, current_depth==max_depth,
                                           max_depth, current_depth+1):
                subclasses.append(subclass)

    return tuple(subclasses)

def serialize_atomic(object, tag_name):
    if object is None:
        return NoneTypeSerializer.serialize(None, tag_name, None)

    object_type = type(object)
    subclass_serializer = None

    # TODO: cache the following loop.
    for serializer in Serializer.subclasses():
        if serializer.serializes is NotImplemented: continue
        if object_type in serializer.serializes:
            return serializer.serialize(object, tag_name, object_type)
        else:
            if serializer.promote_lazy and subclass_serializer:
                    continue
            for serializes in serializer.serializes:
                if issubclass(object_type, serializes):
                    subclass_serializer = (serializer, serializes)
                    break
    if subclass_serializer:
        return subclass_serializer[0].serialize(object, tag_name, subclass_serializer[1])
    else:
        raise NoSuchSerializer(object)

def serialize(object, tag='object', root_tag=None, return_string=True):
    if root_tag:
        element_tree = Element(root_tag)
        element_tree.append(serialize_atomic(object, tag))
    else:
        element_tree = serialize_atomic(object, tag)
    if return_string:
        return elementtree_tostring(element_tree)
    else:
        return element_tree

def serialize_to_file(object, file_, *args, **kwargs):
    close = False
    if not isinstance(file_, file):
        file_ = open(file_, 'w')
        close = True
    file_.write(serialize(object, *args, **kwargs))
    if close:
        file_.close()


def unserialize_atomic(xml_element, typemap=None):
    object_type = xml_element.get('type')

    if typemap:
        object_type = typemap.get(object_type, object_type)

    object_type, unserializer = Serializer.get_for_type(object_type)
    return unserializer.unserialize(xml_element, object_type)

def unserialize(xml_element_tree, has_root=True, *args, **kwargs):
    if has_root:
        if isinstance(xml_element_tree, _ElementTree):
            xml_element_tree = element_tree.getiterator()
        else:
            xml_element_tree = xml_element_tree.getchildren()
    else:
        xml_element_tree = [xml_element_tree]
    return KeyValueIterableSerializer.unserialize_tree(xml_element_tree, dict,
                                                       *args, **kwargs)

def unserialize_file(file_, *args, **kwargs):
    close = False
    if not isinstance(file_, file):
        file_ = open(file_)
        close = True
    result = unserialize(elementtree_fromstring(file_.read()), *args, **kwargs)
    if close:
        file_.close()
    return result

def unserialize_string(string, *args, **kwargs):
    return unserialize(elementtree_fromstring(string), *args, **kwargs)
