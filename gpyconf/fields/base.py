# coding: utf-8
# %FILEHEADER%

# Contains the base classes for gpyconf fields.

from ..mvc import MVCComponent
from .._internal.exceptions import InvalidOptionError

__all__= ('Field',)

class Field(MVCComponent):
    """
    Superclass for all gpyconf fields.

    :param label:
        Label/short description of the presented value (e.g. "Text color:")
    :param label2:
        Second label (not used by all frontends)
    :param default:
        Default field's value. If ``default`` is :const:`None`, the field's
        pre-defined default value is used for default.
    :param blank:
        :const:`True` if blank value should be allowed when saving.
        Defaults to ``False`` for most fields, but there are fields (e.g.
        the :class:`CharField <gpyconf.fields.CharField>`) that set the
        default to :const:`True` to allow empty values as well.
    :param section:
        Section this field belongs to. The frontend should take care
        grouping the fields in sections (e.g. using tabs). A section
        represents the first grouping level.
    :param group:
        Group this field belongs to. The frontend takes care of grouping
        the fields in sections. A group represents the second grouping
        level (after the section).
    :param editable:
        :const:`True` if this field should be editable. Defaults to :const:`True`.
    :param hidden:
        :const:`True` if this field should be hidden (not visible to the user).
        Note that the frontend has to care about hiding a hidden field.
        Defaults to :const:`False`.
    :param kwargs:
        Any other arguments passed to the :meth:`on_initialized` method of
        field subclasses.

    .. note::

        All additional arguments passed to the field constructor have to be
        processed by that field. If there are remaining (unused)
        arguments after that call, a :exc:`TypeError` is raised.

    """
    _abstract = False
    creation_counter = 0
    default = None
    __events__ = (
        'initialized',
        'init-widget',
        'value-changed',
        'reset-value',
        'set-editable'
    )

    is_initialized = False

    def __init__(self, label=None, section=None, default=None, blank=None,
                 editable=True, hidden=False, group=None, label2=None, **kwargs):
        MVCComponent.__init__(self)
        self.update_counter()

        self.label = label
        self.label2 = label2
        self._editable = editable
        self.hidden = hidden
        self.section = section
        self.group = group

        if blank is not None:
            self.blank = blank

        self.connect('initialized', self.on_initialized)
        self.emit('initialized', kwargs)
        self._external_on_initialized(kwargs) # quick n dirty for cream
        if kwargs:
            # there are still kwargs left - either the Field subclass did not
            # pop all kwargs it takes or unexpected kwargs were given.
            # raise a TypeError.
            if len(kwargs) == 1:
                raise TypeError(
                    "%s.__init__ got an unexpected keyword argument %r" \
                    % (self._class_name, kwargs.iterkeys().next())
                )
            else:
                raise TypeError(
                    "%s.__init__ got unexpected keyword arguments %s" \
                    % (self._class_name, ', '.join(kwargs.iterkeys()))
                )

        if default is not None:
            self._user_set_default = self.to_python(default)
        self._value = self.default
        self.is_initialized = True
        # we're done (yes, rlly!)

    def on_initialized(self, sender, kwargs):
        """
        Called after initialization (connected to the `initialized` signal).
        Fields that take additional keyword arguments have to handle their
        stuff here.

        :param kwargs:
            Optional keyword arguments passed to the :meth:`__init__()`
            method. All items of this dictionary have to be deleted
            (recommended is to :meth:`dict.pop()` them) at the end of this
            function (otherwise, a :exc:`TypeError` will be raised,
            see comments in :meth:`Field.__init__()`).
        """
        pass

    def _external_on_initialized(self, kwargs):
        pass

    def update_counter(self):
        # we want the fields exactly in the order we defined them,
        # so we'll need a creation counter because the fields are
        # handled by ConfigurationMeta using dicts (which aren't sorted)
        self.creation_counter = Field.creation_counter
        Field.creation_counter += 1

    def __getattribute__(self, attribute):
        if attribute == 'default':
            if hasattr(self, '_user_set_default'):
                return self._user_set_default
            elif hasattr(self, 'custom_default'):
                return self.custom_default()
        return object.__getattribute__(self, attribute)

    def __setattr__(self, attribute, value):
        if attribute == 'default':
            self._user_set_default = value
        else:
            super(Field, self).__setattr__(attribute, value)

    def get_value(self):
        """ Returns the (pythonic) value of the widget """
        return self._value

    def set_value(self, value):
        """
        Validates ``value`` (using the :meth:`to_python` method) and
        stores it.

        Emits the :signal:`value-changed` signal if the field's value changed.
        """
        if not self.editable:
            raise AttributeError("Can't change value of non-editable field %r"
                % self._class_name)
        value = self.to_python(value)
        emit = value != self.value
        self._value = value
        if emit:
            self.emit('value-changed', self, value)
        return value

    #: The field's current value.
    # Property for :meth:`get_value` and :meth:`set_value`
    value = property(get_value, set_value)

    def isvalid(self):
        """
        Returns :const:`True` if the current value is a valid one
        (returns :const:`False` if the current value is an invalid one).

        .. note::

            If you're building up a custom field and would need to overwrite
            this method, overwrite the :meth:`__valid__` method instead.

        """
        return self.__valid__()

    def __valid__(self):
        """
        (Only for interesting if you're developing your own field)

        Returns :const:`True` if the current field value is valid.
        You can do time-consuming checks like validating an email address
        or an URL here.

        Returns :const:`False` if the current value is invalid.
        """
        return True

    def validation_error(self, faulty=None, *args, **kwargs):
        """
        Raises a :exc:`InvalidOptionError` with ``args`` and ``kwargs``
        """
        allowed_types = self.allowed_types
        if callable(allowed_types):
            allowed_types = allowed_types()
        message = "%(name)s only allows %(allowed)s %(x)s" % {
            'name' : self._class_name,
            'allowed' : allowed_types,
            'x' : '' if faulty is None else " (not %s)" % type(faulty).__name__
        }
        raise InvalidOptionError(self, message, *args, **kwargs)

    def __blank__(self):
        return self.value is None

    def isblank(self):
        """
        Returns :const:`True` if this value is blank (empty).

        .. note::

            If you're building up a custom field and would need to
            overwrite this method, overwrite the :meth:`__blank__` method
            instead.

        """
        return self.__blank__()

    def reset_value(self):
        """ Reset to the field's default value """
        self.value = self.default
        self.emit('reset-value')

    def to_python(self, value):
        """
        Returns ``value`` in a field-compatible form. (This may be, for
        example, a convertion from :class:`int` to :class:`float` or from
        :class:`str` to :class:`unicode`.)

        Calls :meth:`validation_error`
        (which raises a :exc:`InvalidOptionError`)
        with ``value`` as parameter if ``value`` is not compatible to this
        field (is invalid).

        .. warning::
            Do *not* use this method for type checks that consum much time
            (like scheme analyses) because this method may be called, mainly
            depending on the frontend, frequently.
            Use the :meth:`__valid__` (see :meth:`isvalid` documentation)
            method for such purposes.
        """
        return value

    def python_to_conf(self, value):
        """
        Convert ``value`` to :class:`unicode`. This is only used if the backend
        used to store values is running in compatibility mode.

        Subclasses should override this method if conversion is needed.
        """
        return value

    def conf_to_python(self, value):
        """
        Convert ``value`` from  :class:`unicode` to this field's native datatype.
        This is only used if the backend used to store values is running in
        compatibility mode.

        Subclasses should override this method if conversion is needed.
        """
        return value

    def setfromconf(self, value):
        """
        Set the field's value to ``value`` piped through :meth:`conf_to_python`
        """
        self.value = self.conf_to_python(value)

    def get_editable(self):
        return self._editable

    def set_editable(self, value):
        if value != self.editable:
            self.emit('set-editable', value)
        self._editable = value

    #: :const:`True` if this field is editable
    editable = property(get_editable, set_editable)
