from gtk import accelerator_parse, accelerator_valid
from gpyconf.fields import CharField
from gpyconf.frontends._gtk import CharWidget, WIDGET_MAP


class _HotkeyString(unicode):
    def __init__(self, *args, **kwargs):
        unicode.__init__(self, *args, **kwargs)
        self.keyval, self.modifiers = accelerator_parse(self)

class HotkeyField(CharField):
    def to_python(self, value):
        return _HotkeyString(value)

    def __valid__(self):
        return accelerator_valid(*(accelerator_parse(self.value)))


class HotkeyWidget(CharWidget):
    pass



# automagically register all the widgets for the new fields
WIDGET_MAP.update({
    'HotkeyField' : HotkeyWidget
})
