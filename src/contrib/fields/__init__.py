from gpyconf.fields import CharField

class HotkeyField(CharField):
    class _HotkeyString(unicode):
        def __init__(self, *args, **kwargs):
            unicode.__init__(self, *args, **kwargs)

            from gtk import accelerator_parse
            self.keyval, self.modifiers = accelerator_parse(self)

    def to_python(self, value):
        return _HotkeyString(value)

    def __valid__(self):
        from gtk import accelerator_parse, accelerator_valid
        return accelerator_valid(*(accelerator_parse(self.value)))
