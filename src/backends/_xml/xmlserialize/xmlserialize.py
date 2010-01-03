#
#     Copyright (c) 2009 Jonas Haag <jonas@lophus.org>.
#     All rights reserved.
#     License: 2-clause-BSD (Berkley Software Distribution) license
#
#     http://bitbucket.org/Dauerbaustelle/xmlserialize.py
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
__revision__ = '0:e461550045cd'
__all__ = ('serialize', 'unserialize')

try:
    from xml.etree.cElementTree import Element, ElementTree
except ImportError:
    from xml.etree.ElementTree import Element, ElementTree
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO


ITEM_XML_TAG_NAME = 'item'


# Datatype conversion functions
def simple_mapper(_type):
    def encoder(element, obj):
        if isinstance(obj, str):
            obj = obj.decode('utf-8')
        element.text = unicode(obj)

    def decoder(element):
        return _type(element.text) if element.text is not None else _type()

    return encoder, decoder

def none_mapper():
    return lambda *a:None, lambda *a: None

def alias(name):
    def aliasN(n):
        def _alias(*args, **kwargs):
            return HANDLERS[name][n](*args, **kwargs)
        return _alias
    return aliasN(0), aliasN(1)

def list_mapper(_type):
    def encoder(element, obj):
        for item in obj:
            element.append(to_xml_element(ITEM_XML_TAG_NAME, item))

    def decoder(element):
        return _type(to_python_object(o) for o in element.getchildren())

    return encoder, decoder

def dict_mapper():
    def encoder(element, obj):
        for key, value in obj.iteritems():
            element.append(to_xml_element(key, value))

    def decoder(element):
        dct = {}
        for item in element.getchildren():
            dct[item.tag] = to_python_object(item)
        return dct

    return encoder, decoder


HANDLERS = {
    'bool'      : simple_mapper(lambda x:x=='True'),
    'long'      : simple_mapper(long),
    'NoneType'  : none_mapper,
    'int'       : simple_mapper(int),
    'integer'   : alias('int'),
    'unicode'   : simple_mapper(unicode),
    'str'       : alias('unicode'),
    'string'    : alias('unicode'),
    'float'     : simple_mapper(float),
    'list'      : list_mapper(list),
    'set'       : list_mapper(set),
    'frozenset' : list_mapper(frozenset),
    'tuple'     : list_mapper(tuple),
    'dict'      : dict_mapper()
}


class SerializeError(Exception):
    pass

class UnserializeError(Exception):
    pass

def get_handlers_for(type):
    try:
        return HANDLERS[type]
    except KeyError:
        raise SerializeError("Type '%s' not support by xmlserialize.py" % type)

def to_xml_element(name, obj):
    assert isinstance(name, str), "XML tag names must be strings"
    if hasattr(obj, '__xmlserialize__'):
        obj = obj.__xmlserialize__()
    encoder = get_handlers_for(type(obj).__name__)[0]
    element = Element(name, type=type(obj).__name__)
    encoder(element, obj)
    return element

def to_python_object(xml_element):
    return get_handlers_for(xml_element.get('type'))[1](xml_element)


def serialize(dictobj, root_node=None, file=None, encoding=None):
    root_node = Element(root_node or 'root')
    xmltree = ElementTree(root_node)

    for key, value in dictobj.iteritems():
        root_node.append(to_xml_element(key, value))

    buf = StringIO()
    xmltree.write(buf, encoding or 'utf-8')
    buf = buf.getvalue()

    if file is not None:
        file.write(buf)

    return buf


def unserialize(file_or_string):
    from xml.etree.ElementTree import parse as parse_file, fromstring
    if isinstance(file_or_string, file):
        root_node = parse_file(file_or_string).getroot()
    else:
        root_node = fromstring(file_or_string)

    result_dict = {}
    for item in root_node.getchildren():
        result_dict[item.tag] = to_python_object(item)

    return result_dict
