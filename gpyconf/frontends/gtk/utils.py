import os

def dict_to_font_description(_dict):
    from gi.repository.Pango import FontDescription, Style, Weight
    desc = FontDescription()
    desc.set_family(_dict['name'])
    desc.set_size(_dict['size']*1024) # *1024? aha.
    if _dict['italic']:
        desc.set_style(Style.ITALIC)
    if _dict['bold']:
        desc.set_weight(Weight.BOLD)
    return desc

def font_description_to_dict(desc):
    from gi.repository.Pango import FontDescription, Style, Weight
    desc = FontDescription(desc)
    return {
        'name' : desc.get_family(),
        'size' : int(desc.get_size()/1024.0),
        'bold' : desc.get_weight() == Weight.BOLD,
        'italic' : desc.get_style() == Style.ITALIC,
        'underlined' : False
        # TODO
    }

def to_rgb(srgb_tuple):
    """ Converts a three-tuple of SRGB values to RGB values """
    return map(lambda x:int(round(x/257.0)), srgb_tuple)

def joindir(file, *parts):
    return os.path.join(os.path.abspath(os.path.dirname(file)), *parts)
