# %FILEHEADER%
from gi.repository import Gtk as gtk
from gpyconf.mvc import MVCComponent

from .utils import *

def get_widget_for_field(field, mapping=None):
    """
    Looks up for a corresponding :class:`Widget` in ``mapping``
    (Uses the module-default :attr:`WIDGET_MAP` if ``mapping`` is :const:`None`).
    Raises :exc:`KeyError` if no such widget is defined.
    """
    if mapping is None:
        mapping = WIDGET_MAP
    if field._class_name in mapping:
        return mapping[field._class_name](field)
    else:
        raise NotImplementedError("No widget defined for '%s' field. "
            "You could extend the `gpyconf.frontends._gtk.WIDGET_MAP` dict "
            "with your own implementation of a widget for this field "
            "(inherit from `gpyconf.frontends._gtk.Widget`)." % field)


class Widget(MVCComponent):
    """
    Abstract base class for all widgets.

    A widget is used to "display" a field within the window.
    """
    __events__ = ('value-changed',)
    _changed_signal = 'changed'

    def __init__(self, field):
        MVCComponent.__init__(self)

        self.widget = self.gtk_widget()
        self.field_var = field.field_var
        self.label = field.label
        self.label2 = field.label2
        self.widget.connect(self._changed_signal, self.on_value_changed)
        self.initialize()
        self.value = field.value

    def initialize(self):
        """
        Called after initialition. Widgets can to stuff like additional method
        calls here.
        """
        pass

    def on_value_changed(self, sender):
        """
        Value of the :class:`gtk.Widget` changed (mostly through the end user).

        Emits :signal:`value-changed` with :attr:`value` as parameter.
        """
        self.emit('value-changed', self.value)
        log_msg = "Value of %s '%s' changed to '%s'" % (self._class_name,
                                                        self.field_var,
                                                        self.value)
        self.emit('log', log_msg, level='info')

    def get_value(self):
        """
        Returns the widget's value. If the :attr:`prop` attribute is defined,
        tries to return the corresponding :attr:`gtk.Widget.props` attribute.

        If not, :exc:`NotImplementedError` is raised (so this method has to be
        overwritten in that case).
        """
        if hasattr(self, 'prop'):
            return getattr(self.widget.props, self.prop)
        else:
            raise NotImplementedError()

    def set_value(self, value):
        """
        Set the widget's value to ``value``. If the :attr:`prop` attribute is
        defined, tries to set the corresponding :attr:`gtk.Widget.props`
        attribute.

        If not, :exc:`NotImplementedError` is raised (so this method has to be
        overwritten in that case).
        """
        if hasattr(self, 'prop'):
            setattr(self.widget.props, self.prop, value)
        else:
            raise NotImplementedError()

    def to_gtk(self, value):
        """ Converts ``value`` to gtk compatible value """
        return value

    def to_python(self, value):
        """ Converts ``value`` to a standard python value """
        return value

    def _set_value(self, value):
        self.set_value(self.to_gtk(value))

    def _get_value(self):
        return self.to_python(self.get_value())

    #: The current value
    value = property(_get_value, _set_value)


# DEFAULT WIDGETS AND CONTAINERS

class BooleanWidget(Widget):
    gtk_widget = gtk.CheckButton
    prop = 'active'
    _changed_signal = 'toggled'

    def initialize(self):
        self.widget.set_label(self.label)
        self.label = None
        self.label2 = None

class NumberWidget(Widget):
    gtk_widget = gtk.SpinButton
    _changed_signal = 'value-changed'
    prop = 'value'

    def __init__(self, field, digits, step):
        Widget.__init__(self, field)
        self.widget.set_range(float(field.min), float(field.max))
        self.widget.set_digits(digits)
        self.widget.set_increments(step, self.widget.get_increments()[0])
        self.value = field.value
        # setting the value doesn't work before the range/digits setup

class FloatingPointNumberWidget(NumberWidget):
    def __init__(self, field, decimals=None):
        NumberWidget.__init__(self, field, digits=2, step=0.01)

class IntegerWidget(NumberWidget):
    def __init__(self, field):
        NumberWidget.__init__(self, field, digits=0, step=1)

class CharWidget(Widget):
    gtk_widget = gtk.Entry
    prop = 'text'

    def to_python(self, value):
        return unicode(value)

class PasswordWidget(CharWidget):
    def initialize(self):
        self.widget.set_visibility(False)

class IPAddressWidget(CharWidget):
    pass

class URIWidget(CharWidget):
    pass

class URLWidget(URIWidget):
    def to_gtk(self, value):
        from urlparse import urlunparse
        return urlunparse(value)


class FileWidget(URLWidget):
    pass

class EmailAddressWidget(CharWidget):
    pass

class MultiOptionWidget(Widget):
    gtk_widget = gtk.ComboBoxText

    def __init__(self, field):
        self.field = field
        Widget.__init__(self, field)

    def initialize(self):
        for option in self.field.options.keys():
            self.append_entry(option)

    def append_entry(self, label):
        self.widget.append_text(label)

    def get_value(self):
        return self.field.values[self.widget.get_active()]

    def set_value(self, value):
        self.widget.set_active(self.field.values.index(value))

class ColorWidget(Widget):
    gtk_widget = gtk.ColorButton
    prop = 'color'
    _changed_signal = 'color-set'

    def to_python(self, value):
        return to_rgb((value.red, value.green, value.blue))

    def to_gtk(self, value):
        return gtk.gdk.color_parse(value.to_string())

class FontWidget(Widget):
    gtk_widget = gtk.FontButton
    _changed_signal = 'font-set'
    prop = 'font-name'

    def to_gtk(self, value):
        return dict_to_font_description(value)

    def to_python(self, value):
        return font_description_to_dict(value)


class DateTimeWidget(CharWidget):
    pass

class TextWidget(CharWidget):
    pass


WIDGET_MAP = {
    'BooleanField'      : BooleanWidget,
    'CharField'         : CharWidget,
    'PasswordField'     : PasswordWidget,
    'IPAddressField'    : IPAddressWidget,
    'URIField'          : URIWidget,
    'URLField'          : URLWidget,
    'FileField'         : FileWidget,
    'EmailAddressField' : EmailAddressWidget,
    'IntegerField'      : IntegerWidget,
    'FloatField'      : FloatingPointNumberWidget,
    'MultiOptionField'  : MultiOptionWidget,
    'ColorField'        : ColorWidget,
    'DateTimeField'     : DateTimeWidget,
    'FontField'         : FontWidget,
    'TextField'         : TextWidget
}
