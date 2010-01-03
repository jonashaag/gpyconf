# coding: utf-8
from gpyconf import Configuration, fields
from gpyconf.backends._xml import XMLBackend

class Conf(Configuration):
    backend = XMLBackend

    a = fields.DictField()
    b = fields.DictField(keys={'a_dict' : dict, 'a_list' : list, 'a_int' : int})

    c = fields.ListField()
    d = fields.ListField(item_type=dict)

c = Conf()
c.a = c_a = {
    'aasdasd' : (1,2,3),
    'asd' : u'baaaräää',
    # this can't work in XML:
    # 5: 'elf',
    # 4 : 42.4222
}

c.c = c_c = ['a', 'b', {'foo' : 'bar'}, {'baz': 1, 'peng': 2}]

c.d = c_d = [{'a': 1, 'b':2},  {'c':3, 'd':'foo'}]

c.b = c_b = {
    'a_dict' : c.a,
    'a_list' : c.c,
    'a_int' : 42
}

c.save()

#from xml.dom.minidom import parse
#print parse(c.backend_instance.file).toprettyxml()

del c

c = Conf()
assert c.a == c_a
assert c.b == c_b
assert c.c == c_c
assert c.d == c_d
