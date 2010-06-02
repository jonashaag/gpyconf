# %FILEHEADER%
"""
gpyconf GTK+ frontend
---------------------

Every :class:`Field <gpyconf.fields.base.Field>` is mapped to a :class:`Widget`,
which handles interaction between GTK widgets and gpyconf fields.
That mapping is defined in :attr:`widget.WIDGET_MAP`.

Sections are separated using tabs.

Custom widgets to be added to the mapping have to be inherited from the
:class:`Widget` base class and have to implement all documented methods.
"""
import os
import gtk

from gpyconf.frontends import Frontend
from widgets import get_widget_for_field
from .utils import *

class ConfigurationOption(object):

    def __init__(self, widget, label=None, post_label=None):

        self.widget = widget
        self.label = label
        self.post_label = post_label

        self.interface = gtk.Builder()
        self.interface.add_from_file(joindir(__file__, 'interface/option.ui'))

        self.label_container = self.interface.get_object('label_container')
        self.post_label_container = self.interface.get_object('post_label_container')
        self.widget_container = self.interface.get_object('widget_container')

        self.widget_container.add(self.widget)
        if self.label:
            label = gtk.Label(self.label)
            label.set_alignment(0, .5)
            self.label_container.add(label)
        if self.post_label:
            post_label = gtk.Label(self.post_label)
            post_label.set_alignment(0, .5)
            self.post_label_container.add(post_label)


class ConfigurationGroup(object):

    def __init__(self, title=None):

        self.options = {}

        self.title = title

        self.interface = gtk.Builder()
        self.interface.add_from_file(joindir(__file__, 'interface/group.ui'))

        self.group = self.interface.get_object('group')
        self.table = self.interface.get_object('table')

        if self.title:
            self.label = gtk.Label()
            self.label.set_alignment(0, .5)
            self.label.set_markup('<span weight="bold">{0}</span>'.format(self.title))
            self.group.pack_start(self.label, True, False, 5)
            self.group.reorder_child(self.label, 0)


    def append_option(self, option):

        row = len(self.options)
        self.table.resize(len(self.options), 2)

        if option.label and not option.post_label:
            self.table.attach(option.label_container, 0, 1, row, row+1)
            self.table.attach(option.widget_container, 1, 2, row, row+1, xoptions=gtk.FILL)
        elif option.label and option.post_label:
            box = gtk.HBox()
            box.set_spacing(10)
            box.pack_start(option.label_container, expand=False)
            box.pack_start(option.widget_container, expand=False)
            box.pack_start(option.post_label_container, expand=False)
            self.table.attach(box, 0, 2, row, row+1, xoptions=gtk.FILL)
        else:
            self.table.attach(option.widget_container, 0, 2, row, row+1, xoptions=gtk.FILL)


    def add_field(self, field):

        opt = ConfigurationOption(field.widget.widget,
                                  field.widget.label,
                                  field.widget.label2)
        self.options[field.field_var] = opt
        self.append_option(opt)


class ConfigurationSection(object):

    def __init__(self, title=None):

        self.groups = {}

        self.title = title

        self.interface = gtk.Builder()
        self.interface.add_from_file(joindir(__file__, 'interface/section.ui'))

        self.section = self.interface.get_object('section')
        self.layout = self.interface.get_object('layout')


    def append_group(self, group):
        self.section.pack_start(option.group, True, False, 0)


    def add_field(self, field):
        group = self.groups.get(field.group)
        if group is None:
            self.groups[field.group] = group = ConfigurationGroup(title=field.group)
            self.layout.pack_start(group.group, False, False, 5)
        group.add_field(field)


class ConfigurationDialog(Frontend):

    def __init__(self, backref, fields, title=None, ignore_missing_widgets=False):

        Frontend.__init__(self)

        self.sections = {}
        self.widgets = {}

        self.interface = gtk.Builder()
        self.interface.add_from_file(joindir(__file__, 'interface/dialog.ui'))

        self.dialog = self.interface.get_object('dialog')
        self.layout = self.interface.get_object('layout')
        self.content = self.interface.get_object('content')

        if title:
            self.dialog.set_title(title)

        for name, field in fields.iteritems():
            if field.hidden: continue
            self.add_field(field, ignore_missing_widgets)


    def add_field(self, field, ignore_missing_widgets):

        try:
            field.widget = get_widget_for_field(field)
        except NotImplementedError:
            # TODO: Eliminate.
            if ignore_missing_widgets:
                return
            else:
                raise

        section = self.sections.get(field.section)
        if section is None:
            self.sections[field.section] = section = ConfigurationSection()
            if field.section:
                self.content.append_page(section.section, gtk.Label(field.section))
            else:
                self.content.insert_page(section.section, gtk.Label("General"), position=0)
            self.content.set_current_page(0)

        if self.content.get_n_pages() > 1:
            self.content.set_show_tabs(True)
            self.content.set_show_border(True)

        section.add_field(field)

        field.connect('value-changed', self.on_field_value_changed)
        field.widget.connect('log', self.on_widget_log)
        field.widget.connect('value-changed', self.on_widget_value_changed)

        if not field.editable:
            field.widget.widget.set_sensitive(False)

        self.widgets[field.field_var] = field.widget


    def on_field_value_changed(self, sender, field_instance, new_value):
        self.widgets[field_instance.field_var].value = new_value


    def on_widget_value_changed(self, sender, new_value):
        self.emit('field-value-changed', sender.field_var, new_value)


    def on_widget_log(self, sender, msg, level='info'):
        self.emit('log', msg, level=level)


    def run(self):

        self.dialog.show_all()
        response = self.dialog.run()
        self.close(save=response==gtk.RESPONSE_CLOSE)


    def close(self, save=False):

        self.emit('close')
        if save:
            try:
                self.emit('save')
            except InvalidOptionError, e:
                # TODO: Some error displaying here.
                self.run()
        self.emit('closed')


if __name__ == '__main__':
    from gpyconf.fields import ColorField
    f1 = ColorField(
        label = "Background Color",
        section = "Foo Section",
        group = "Bar Group",
    )
    f1.field_var = 'foo'


    f2 = ColorField(
        group = "Bar Group",
    )
    f2.field_var = 'bar'

    dialog = ConfigurationDialog()
    dialog.add_field(f1)
    dialog.add_field(f2)

    dialog.run()
