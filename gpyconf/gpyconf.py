# coding: utf-8
# %FILEHEADER%
"""
    The :mod:`gpyconf` module
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    The :mod:`gpyconf` module contains gpyconf's default Controller, the
    :class:`Configuration` class. It takes care of communication between
    frontend and backend and offers an interface to "the developer".

    The API is very minimalistic and easy to use. To get information on how to
    define configuration models and access fields and fields' values, refer to
    the :doc:`/usage` section.

    API documentation
    -----------------
"""
import weakref
from . import fields, backends, frontends
from .mvc import MVCComponent
from ._internal import logging, dicts
from ._internal import exceptions
from ._internal.exceptions import InvalidOptionError

__all__ = ('fields', 'backends', 'frontends', 'exceptions', 'Configuration')


class Proxy(object):
    def __setattr__(self, attribute, value):
        if attribute == '_proxy_obj':
            object.__setattr__(self, attribute, value)
        else:
            self._proxy_obj.__setattr__(attribute, value)

    def __getattr__(self, attribute):
        return self._proxy_obj.__getattribute__(attribute)

class DefaultBackend(Proxy):
    def __init__(self, *args, **kwargs):
        from .backends import configparser
        self._proxy_obj = configparser.ConfigParserBackend(*args, **kwargs)

class DefaultFrontend(Proxy):
    def __init__(self, *args, **kwargs):
        from .frontends import gtk
        self._proxy_obj = gtk.ConfigurationDialog(*args, **kwargs)


class ConfigurationMeta(type):
    """ Metaclass for the :class:`Configuration` class """
    def __new__(cls, cls_name, cls_bases, cls_dict):
        super_new = super(ConfigurationMeta, cls).__new__
        parents = tuple(base for base in cls_bases
                        if isinstance(base, ConfigurationMeta))
        if not parents:
            # This isn't a subclass of ConfigurationMeta, don't do anything special
            return super_new(cls, cls_name, cls_bases, cls_dict)

        class_fields = cls_dict['fields'] = dicts.FieldsDict()

        for superclass in parents:
            for name, field in superclass.fields.iteritems():
                class_fields[name] = field
                field.field_var = name

        new_fields = list()
        for name, obj in cls_dict.items():
            if isinstance(obj, fields.Field):
                new_fields.append((name, cls_dict.pop(name)))

        new_fields.sort(key=lambda item:item[1].creation_counter)
        for name, field in new_fields:
            class_fields[name] = field
            field.field_var = name

        return super_new(cls, cls_name, cls_bases, cls_dict)


class Configuration(MVCComponent):
    """
    gpyconf's controller class. The :class:`Configuration` class acts between
    the backend and the frontend; it makes the backend load its stored
    values and passes them to the frontend and the other way round.

    All keyword arguments passed will result in attributes, so calling the
    call like this ::

        conf_instance = MyConfiguration(foo=42, bar='bazz')

    would set the :attr:`foo` attribute to 42 and the :attr:`bar` to 'bazz'.
    With this, you can also change the used frontend or backend *at runtime*::

        conf_instance = MyConfiguration(frontend=MyGreatWebInterface,
                                        backend=MyGreatSQLiteBackend)

    The signals :signal:`field-value-changed`, :signal:`frontend-initialized`,
    :signal:`pre-read`, :signal:`pre-save`, :signal:`pre-reset` and
    :signal:`initialized` should be self-speaking.

    The signature for a callback connecting to :signal:`field-value-changed` is
    the following::

        def callback(sender_instance, field_instance, new_field_value):
            ...
    """
    __metaclass__ = ConfigurationMeta
    fields = dict()

    frontend_instance = None
    initially_read = False
    logger = None
    logging_level = 'warning'

    #: The :doc:`backend <backends>` to use
    backend = DefaultBackend
    #: The :doc:`frontend <frontends>` to use
    frontend = DefaultFrontend

    __events__ = (
        'field-value-changed',
        'frontend-initialized',
        'pre-read',
        'pre-save',
        'pre-reset',
        'initialized'
    )

    def __init__(self, read=True, **kwargs):
        MVCComponent.__init__(self)
        for key, value in kwargs.iteritems():
            setattr(self, key, value)

        if self.logger is None:
            self.logger = logging.Logger(self._class_name, self.logging_level)
        self.logger.info("Logger initialized (%s)" % self.logger)

        if not hasattr(self, 'backend_instance'):
            self.backend_instance = self.backend(weakref.ref(self))
        self.backend_instance.connect('log', self.backend_log)

        self.logger.info("Backend initialized (%s)" % self.backend)

        for name, instance in self.fields.iteritems():
            instance.connect('value-changed', self.on_field_value_changed)

        self.emit('initialized')
        if read:
            self.read()
        # read the config andd set it to the fields.

    def on_field_value_changed(self, sender, field, new_value):
        self.emit('field-value-changed', field.field_var, new_value)


    # MAGIC/API:
    def __setattr__(self, attr, value):
        # if ``attr`` is a field, don't overwrite the field but its value
        if attr in self.fields:
            return self.fields[attr].set_value(value)
        else:
            super(Configuration, self).__setattr__(attr, value)

    def __getattr__(self, name):
        try:
            return self.fields[name].value
        except KeyError:
            raise AttributeError("No such attribute '%s'" % name)


    # BACKEND:
    def save(self, save=True):
        """
        Checks for every field wether it's value is valid and not emtpy;
        if the value is invalid or empty and the field was not marked to allow
        blank values, an
        :exc:`InvalidOptionError <gpyconf._internal.exceptions.InvalidOptionError>`
        will be raised.

        Otherwise, passes the fields' values to the backend. If the ``save``
        argument is set :const:`True`, makes the backend store the values
        permanently.
        """
        self.logger.debug("Saving option values...")
        if self.backend_instance.compatibility_mode:
            self.logger.info("Backend runs in compatibility mode")

        for name, field in self.fields.iteritems():
            if not field.editable:
                # not editable, ignore
                continue
            if field.isblank():
                self.logger.info('Is blank', field=field)
                if not field.blank:
                    # blank, but blank values are not allowed, raise error
                    raise InvalidOptionError("The option '%s' wasn't set yet" \
                        % name + " (is None). Use blank=True to safe anyway.")
                value = None
            else:
                # not blank, validate
                if not field.isvalid():
                    self.logger.error("Invalid option '%s'" % field.value,
                                      field=field)
                    field.validation_error(field.value)
                value = field.value

            # if backend runs in compatibility mode, convert to str type:
            if self.backend_instance.compatibility_mode:
                if value is None:
                    value = u''
                else:
                    _value = value
                    value = field.python_to_conf(value)
                if not isinstance(value, unicode):
                    self.logger.warning("Wrong datatype conversion: "
                        "Got %s, not unicode" % type(value), field=field)

            self.backend_instance.set_option(name, value)

        if save:
            self._save()

    def _save(self):
        self.emit('pre-save')
        self.backend_instance.save()

    def read(self):
        """
        Reads the configuration options from the backend and updates the
        fields' values
        """
        self.logger.debug("Reading option values...")
        self.emit('pre-read')
        if not self.initially_read:
            self.backend_instance.read()
            self.initially_read = True
        for field, value in self.backend_instance.tree.iteritems():
            try:
                if self.backend_instance.compatibility_mode:
                    self.logger.info("Datatype conversion of '%s'" % field)
                    self.fields[field].setfromconf(value)
                else:
                    self.fields[field].value = value
            except KeyError:
                self.logger.warning("Got an unexpected option name '%s' "
                    "(No field according to configuration option '%s')" % \
                        (field, field))

    def reset(self):
        """ Resets all configuration options """
        self.logger.debug("Resetting option values...")
        self.emit('pre-reset')
        self.backend_instance.reset_all()
        map(lambda field:field.reset_value(), self.fields.values())
        self.read()


    # FRONTEND:
    def get_frontend(self):
        """
        Returns a (new) instance of the specified :attr:`frontend`
        """
        if self.frontend_instance is None:
            self.logger.info("Using '%s' as frontend" % (self.frontend.__name__))
            # initialize the frontend:
            self._init_frontend(self.fields)
            self.frontend_instance.connect('save', self.frontend_save)
            self.frontend_instance.connect('log', self.frontend_log)

            self.logger.info("Initialized frontend (%s)" % self.frontend)

            self.frontend_instance.connect('field-value-changed',
                self.frontend_field_value_changed)

            self.emit('frontend-initialized')
        return self.frontend_instance

    def _init_frontend(self, fields):
        """
        Instantiates the :attr:`frontend` passing all ``fields`` as parameter
        and stores it the instance in the :attr:`frontend_instance` attribute.

        Only interesting for developers who want to overwrite the default
        :class:`Configuration` class.
        """
        self.frontend_instance = self.frontend(weakref.ref(self), fields)

    def run_frontend(self):
        """
        Runs (shows) the frontend, waits for the frontend to quit, reads
        values and saves them if the frontend tells to.
        """
        self.logger.debug("Running frontend...")
        self.get_frontend().run()

    def frontend_field_value_changed(self, sender, field_name, new_value):
        setattr(self, field_name, new_value)

    def frontend_log(self, sender, msg, level):
        getattr(self.logger, level)("Frontend: %s" % msg)

    def frontend_save(self, sender):
        self.save()


    # BACKEND:
    def backend_log(self, sender, msg, level):
        getattr(self.logger, level)("Backend: %s" % msg)
