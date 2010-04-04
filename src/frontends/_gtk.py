# %FILEHEADER%
"""
    gpyconf GTK+ frontend
    ---------------------

    Every :class:`Field <gpyconf.fields.base.Field>` is mapped to a :class:`Widget`,
    which handles interaction between GTK widgets and gpyconf fields.
    That mapping is defined in :attr:`WIDGET_MAP`.

    Widgets are placed in a :class:`WidgetContainer`. Fields are grouped by
    their :attr:`group <gpyconf.fields.base.Fields.group>` attribute. Grouped
    widgets will not be added to the :class:`WidgetContainer` directly, but
    over a :class:`GroupContainer`. Widgets without a group are added directly
    to the container. Widgets that are grouped will be added to the group
    container. That group container will then be added to the widget container
    using the :meth:`append_group <WidgetContainer.append_group>` method.
    By default, the :class:`WidgetTable` and :class:`Group` classes are used.

    The widget container will be added to the :class:`window <GtkConfigurationWindow>`.
    Sections are separated using tabs.

    You can overwrite the used containers using the
    :attr:`container <GtkConfigurationWindow.container>` and
    :attr:`group_container <GtkConfigurationWindow.group_container>` arguments.
    Arguments with the very same names may also be passed to the constructor of
    :class:`GtkConfigurationWindow`; this has the same effect as changing the
    attributes manually.

    The widget map may be overwritten or extended at window instance levels using the
    :meth:`register_widget_for_field <GtkConfigurationWindow.register_widget_for_field>`
    method. If you want to change the mapping at module level, simply modify
    the :attr:`WIDGET_MAP` dictionary.

    Custom widgets to be added to the mapping have to be inherited from the
    :class:`Widget` base class and have to implement all documented methods.
"""
from ..events import GSignals
from .._internal.dicts import ordereddefaultdict
from .._internal.exceptions import InvalidOptionError
from . import Frontend
import gtk

DEFAULT_SECTION_NAME = 'General'
UNGROUPED = object()


# UTILS

def dict_to_font_description(_dict):
    from pango import FontDescription, STYLE_ITALIC, WEIGHT_BOLD
    desc = FontDescription()
    desc.set_family(_dict['name'])
    desc.set_size(_dict['size']*1024) # *1024? aha.
    if _dict['italic']:
        desc.set_style(STYLE_ITALIC)
    if _dict['bold']:
        desc.set_weight(WEIGHT_BOLD)
    return desc

def font_description_to_dict(desc):
    from pango import FontDescription, STYLE_ITALIC, WEIGHT_BOLD
    desc = FontDescription(desc)
    return {
        'name' : desc.get_family(),
        'size' : int(desc.get_size()/1024.0),
        'bold' : desc.get_weight() == WEIGHT_BOLD,
        'italic' : desc.get_style() == STYLE_ITALIC,
        'underlined' : False
        # TODO
    }

def to_rgb(srgb_tuple):
    """ Converts a three-tuple of SRGB values to RGB values """
    return map(lambda x:int(round(x/257.0)), srgb_tuple)

def defaultdict_factory(defaulttype):
    def factory():
        return ordereddefaultdict(defaulttype)
    return factory

def section_group_tree(fields):
    # Returns a tree like this:
    # {
    #   'section1' : {
    #       'group1' : [field1, field2, field3],
    #       'group2' : [field4, field5, field6],
    #       UNGROUPED : [field7, field8]
    #    },
    #    'section2' : ...
    # }
    from collections import defaultdict
    sections = ordereddefaultdict(defaultdict_factory(list))
    for name, field in fields.iteritems():
        if field.hidden: continue
        # ignore hidden fields
        sections[field.section or DEFAULT_SECTION_NAME] \
                [field.group or UNGROUPED].append(field)
    return sections

def get_widget_for_field(field, mapping=None):
    """
    Looks up for a corresponding :class:`Widget` in ``mapping``
    (Uses the module-default :attr:`WIDGET_MAP` if ``mapping`` is :const:`None`).
    Raises :exc:`KeyError` if no such widget is defined.
    """
    if mapping is None:
        mapping = WIDGET_MAP
    if field.name in mapping:
        return mapping[field.name](field)
    else:
        raise NotImplementedError("No widget defined for '%s' field. "
            "You could extend the `gpyconf.frontends._gtk.WIDGET_MAP` dict "
            "with your own implementation of a widget for this field "
            "(inherit from `gpyconf.frontends._gtk.Widget`)." % field)


# BASE CLASSES

class WidgetContainer(object):
    """
    Container for widgets.
    """
    def append(self, child, label=None, label2=None):
        """
        Appends ``child`` (which is a :class:`gtk.Widget`)
        to the end of the container.
        """
        raise NotImplementedError()

    def append_group(self, container):
        """
        Appends a group ``container`` to the end of the container.
        """
        raise NotImplementedError()

class GroupContainer(object):
    """
    Container for a group.

    :param name: The group's name
    """
    def __init__(self, name):
        self.name = name

    def append(self, child, label=None, label2=None):
        """
        Appends ``child`` (which is a :class:`gtk.Widget`)
        to the end of the container.
        """
        raise NotImplementedError()

class Widget(GSignals):
    """
    Abstract base class for all widgets.

    A widget is used to "display" a field within the window.
    """
    __events__ = ('value-changed', 'log')
    _changed_signal = 'changed'

    def __init__(self, field):
        GSignals.__init__(self)
        self.widget = self.widget()
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
        self.emit('log', "Value of %s '%s' changed to '%s'" % (
            self.__class__.__name__, self.field_var, self.value), level='info')

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
    widget = gtk.CheckButton
    prop = 'active'
    _changed_signal = 'toggled'

    def initialize(self):
        self.widget.set_label(self.label)
        self.label = None
        self.label2 = None

class FloatingPointNumberWidget(Widget):
    widget = gtk.SpinButton
    _changed_signal = 'value-changed'
    prop = 'value'

    def __init__(self, field, decimals=None):
        Widget.__init__(self, field)
        self.widget.set_range(float(field.min), float(field.max))
        self.widget.set_increments(float(field.step),
                                   self.widget.get_increments()[0])
        self.widget.set_digits(field.decimals if decimals is None else decimals)

        self.value = field.value
        # setting the value doesn't work before the range/digits setup

class IntegerWidget(FloatingPointNumberWidget):
    def __init__(self, field):
        FloatingPointNumberWidget.__init__(self, field, decimals=0)

class CharWidget(Widget):
    widget = gtk.Entry
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
    widget = gtk.combo_box_new_text

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
    widget = gtk.ColorButton
    prop = 'color'
    _changed_signal = 'color-set'

    def to_python(self, value):
        return to_rgb((value.red, value.green, value.blue))

    def to_gtk(self, value):
        return gtk.gdk.color_parse(value.to_string())

class FontWidget(Widget):
    widget = gtk.FontButton
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


class LeftAlignedLabel(gtk.Label):
    def __init__(self, *args, **kwargs):
        gtk.Label.__init__(self, *args, **kwargs)
        self.set_alignment(0.0, 0.5)


class WidgetTable(WidgetContainer, gtk.Alignment):
    """
    An area used to display widgets within a :class:`gtk.Table`.
    """
    # TODO: WHY on earth did I use a gtk.Alignment here?!
    def __init__(self, rows=1, add_table=True, border_width=12):
        gtk.Alignment.__init__(self)
        self.rows_left = rows
        self.rows = rows
        self.table = gtk.Table(rows, columns=2)
        self.table.set_border_width(border_width)
        self.table.set_col_spacings(6)
        self.table.set_row_spacings(6)
        self.table.set_row_spacing(0, 0)

        self.set_property('xscale', 1.0)
        self.set_property('yscale', 1.0)

        if add_table:
            self.add(self.table)

    def insert(self, child, row, label=None, label2=None):
        """
        Inserts ``child`` in ``row``. If ``label`` is not :const:`None`,
        puts that ``label`` in the first column and the ``child`` in the second.
        If ``label`` is :const:`None`, spans ``child`` over both columns.

        :return: A :class:`tuple` containg the row and the first column
                 ``child`` was attached to.
        """
        column = 0
        self.rows += 1
        if self.rows_left < 1:
            self.table.resize(self.rows, 2)
        else:
            self.rows_left -= 1

        if label2 is not None:
            # two labels set, use colspanning (label1 | widget | label2)
            box = gtk.HBox()
            box.set_spacing(12)
            box.pack_start(LeftAlignedLabel(label), expand=False)
            box.pack_start(child, expand=False)
            box.pack_start(LeftAlignedLabel(label2), expand=False)
            child = box
            label = None

        if label is not None:
            label = LeftAlignedLabel(label)
            self.table.attach(label, column, column+1, row, row+1)
            self.table.attach(child, column+1, column+2, row, row+1)
        else:
            self.table.attach(child, column, column+2, row, row+1)

        return row, column

    def append(self, child, label=None, label2=None):
        """ Inserts ``child`` at the end of the table """
        self.insert(child, self.rows, label=label, label2=label2)

    def insert_group(self, group, row):
        """ Insert :class:`Group` instance at ``row`` """
        self.insert(group, row)

    def append_group(self, group):
        """ Insert :class:`Group` instance at the end """
        self.insert_group(group, self.rows)

class Group(WidgetTable):
    # TODO append stuff doesn't work inheriting from GroupContainer
    """ Wrapper for grouped widgets """
    def __init__(self, name, rows=1):
        WidgetTable.__init__(self, rows, add_table=False, border_width=6)
        self._name = name
        self.box = gtk.VBox()
        self.label = LeftAlignedLabel()
        self.label.set_use_markup(True)
        self.label.set_markup('<b>%s</b>' % self._name)

        self.box.pack_start(self.label, False, False)
        self.box.pack_start(self.table)

        self.set_property('bottom-padding', 6)
        self.add(self.box)


# THE WINDOW

class GtkConfigurationWindow(Frontend):
    """
    A :mod:`gtk` based configuration window.
    """
    #: The container to put widgets into (defaults to :class:`WidgetTable`)
    container = WidgetTable
    #: The container to put grouped widgets into (defaults to :class:`Group`)
    group_container = Group

    def __init__(self, backref, fields, title=None, container=None,
                 group_container=None, ignore_missing_widgets=False):
        Frontend.__init__(self)

        self.title = title
        self.ignore_missing_widgets = ignore_missing_widgets
        self._tab_name_map = {}
        self._widget_map = {}
        self.widgets = {}

        if container is not None:
            self.container = container
        if group_container is not None:
            self.group_container = group_container

        self.build_ui()
        self.add_fields(fields)

    def build_ui(self):
        """
        Builds the UI. Subclasses may overwrite this method if they offer a
        congruent API. This means, they have to implement both the
        :attr:`_dialog` and the :attr:`_widgets` attributes as objects
        that offer :class:`gtk.Dialog` and :class:`gtk.Notebook` compatible
        APIs.

        .. tip::
            Before going to use ugly hacks making your UI classes being
            compatible to those APIs just go and build your frontend from
            bottom up -- it doesn't hurt.
        """
        self._dialog = gtk.Dialog(buttons=(gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE))
        if self.title is not None:
            self._dialog.set_title(self.title)
        self._widgets = gtk.Notebook()

        self._dialog.vbox.pack_start(self._widgets)

    def register_widget_for_field(self, field_name, widget_class):
        """
        Registers ``widget_class`` as corresponding widget class
        for ``field_name`` classes.
        This should be used to "register" third-party widgets for
        fields not supported by the gtk frontend. It can be used
        to overwrite the widet mappings, too.
        """
        self._widget_map[field_name] = widget_class

    def add_fields(self, fields):
        # TODO: Unreadable loops.
        tree = section_group_tree(fields)
        for section, groups in tree.iteritems():
            table = self._tab_by_name(section)
            for group, fields in groups.iteritems():
                if group is UNGROUPED:
                    insert_to = table
                else:
                    insert_to = self.group_container(group)
                    table.append_group(insert_to)
                for field in fields:
                    try:
                        widget = get_widget_for_field(field, self._widget_map)
                    except NotImplementedError:
                        try:
                            widget = get_widget_for_field(field)
                        except NotImplementedError:
                            if self.ignore_missing_widgets: continue
                            else: raise
                    field.connect('value-changed', self.on_field_value_changed)
                    widget.connect('value-changed', self.on_widget_value_changed)
                    widget.connect('log', self.on_widget_log)
                    if not field.editable:
                        widget.widget.set_sensitive(False)
                    insert_to.append(widget.widget, widget.label, widget.label2)
                    self.widgets[field.field_var] = widget

    def _tab_by_name(self, name):
        """
        Returns or (if needed) creates a new notebook tab ``name`` which
        contains a :attr:`container` to display widgets.
        """
        tab = self._tab_name_map.get(name)
        if tab is None:
            table = self.container()
            label = gtk.Label(name)
            con = gtk.Alignment()
            con.add(table)
            self._tab_name_map[name] = self._widgets.append_page(con, label)
            return table
        return self._widgets.get_nth_page(tab)

    def on_field_value_changed(self, sender, field, new_value):
        self.widgets[field.field_var].value = new_value

    def on_widget_value_changed(self, sender, new_value):
        self.emit('field-value-changed', sender.field_var, new_value)

    def on_widget_log(self, sender, msg, level='info'):
        self.emit('log', msg, level=level)

    def run(self):
        self._dialog.show_all()
        response = self._dialog.run()
        self.close(response==gtk.RESPONSE_CLOSE)

    def close(self, save=False):
        self.emit('close')
        if save:
            try:
                self.emit('save')
            except InvalidOptionError, e:
                self.run()
        self.emit('closed')
