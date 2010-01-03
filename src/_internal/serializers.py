# TODO: see wether non-printable ASCII SEQUENCEs work with JSON/ConfigParser/...
# -> if yes, prefer those over the following sequences.
LIST_JOIN_SEQUENCE           = '[:NEXT ITEM:]'
DICT_KEY_VALUE_JOIN_SEQUENCE = '[:VALUE:]'
DICT_PAIR_JOIN_SEQEUNCE      = '[:NEXT PAIR:]'

def _(o):
    return map(lambda x:unicode(x) if not isinstance(x, bool)
                                   else unicode(int(x)), o)

def serialize_list(list):
    """ Serializes a list/tuple/iterable to a string. """
    return LIST_JOIN_SEQUENCE.join(_(list))

def unserialize_list(string, itemtype=str):
    """
    Unserializes a serialized list/tuple/iterable to a list
    using ``itemtype`` as type for each item.
    """
    if itemtype is None: itemtype = lambda *x:None
    if not string: return [itemtype()]
    if itemtype is bool: itemtype = lambda x:bool(int(x))
    return map(itemtype, string.split(LIST_JOIN_SEQUENCE))

def serialize_dict(dict):
    """ Serializes a dict to a string """
    return DICT_PAIR_JOIN_SEQEUNCE.join(
                DICT_KEY_VALUE_JOIN_SEQUENCE.join(_((k, v))) for k, v
           in dict.iteritems())

def unserialize_dict(string, typemap=None):
    """
    Unserializes a serialized dict to a dict
    using value types for keys defined in ``typemap``.
    """
    typemap = typemap or {}
    if not string: return typemap
    def fixbool(type):
        if type is bool: return lambda x:bool(int(x))
        else: return type
    return dict((k, fixbool(typemap.get(k, str))(v)) for k, v in
                (pair.split(DICT_KEY_VALUE_JOIN_SEQUENCE) for pair in
                 string.split(DICT_PAIR_JOIN_SEQEUNCE)))
