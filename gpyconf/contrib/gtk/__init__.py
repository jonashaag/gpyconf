import time
from gi.repository import Gtk as gtk, Gdk as gdk, GObject as gobject
from gpyconf.fields import CharField
from gpyconf.frontends.gtk.widgets import Widget, WIDGET_MAP


class _HotkeyString(unicode):
    def __new__(cls, *args, **kwargs):
        self = unicode.__new__(cls, *args, **kwargs)
        self.keyval, self.modifiers = gtk.accelerator_parse(self)
        return self

class HotkeyField(CharField):
    def __init__(self, action=None, *args, **kwargs):
        CharField.__init__(self, *args, **kwargs)
        self.action = action

    def to_python(self, value):
        return _HotkeyString(value)

    def __valid__(self):
        return gtk.accelerator_valid(*(gtk.accelerator_parse(self.value)))

class HotkeyButton(gtk.Button):

    __gtype_name__ = 'HotkeyButton'
    __gsignals__ = {
        'changed': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
    }

    def __init__(self):

        gtk.Button.__init__(self)

        self.value = None

        self.dialog = gtk.Dialog(None, None, gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT | gtk.DIALOG_NO_SEPARATOR,
                     (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT))
        self.dialog.set_position(gtk.WIN_POS_CENTER_ALWAYS)

        self.dialog_content = self.dialog.get_content_area()
        self.dialog_content.pack_start(gtk.Label("Please press a hotkey combination..."), True, True, 10)
        self.dialog.connect("key-press-event", self.dialog_key_press_cb)

        self.connect('clicked', self.clicked_cb)


    def clicked_cb(self, source):

        self.dialog.show_all()
        while gtk.gdk.keyboard_grab(self.dialog.window) != gtk.gdk.GRAB_SUCCESS:
            time.sleep (0.1)
        self.dialog.run()
        self.dialog.hide()


    def dialog_key_press_cb(self, source, event):

        keyval = event.keyval
        modifier_mask = event.state & gtk.accelerator_get_default_mod_mask()

        if gtk.accelerator_valid(keyval, modifier_mask):
            self.set_value(gtk.accelerator_name(keyval, modifier_mask))
            self.emit('changed')
            gtk.gdk.keyboard_ungrab(gtk.get_current_event_time())
            self.dialog.hide()


    def set_value(self, value):

        self.value = value
        self.set_label(gtk.accelerator_get_label(*gtk.accelerator_parse(value)))


class HotkeyWidget(Widget):

    gtk_widget = HotkeyButton

    def __init__(self, field):

        Widget.__init__(self, field)


    def set_value(self, value):

        self.widget.set_value(value)


    def get_value(self):

        return self.widget.value


# automagically register all the widgets for the new fields
WIDGET_MAP.update({
    'HotkeyField' : HotkeyWidget
})
