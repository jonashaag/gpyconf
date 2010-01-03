# coding: utf-8
# %FILEHEADER%

from itertools import izip
from ..mvc import MVCComponent
from .._internal.utils import NONE
from .._internal.exceptions import MissingOption

class Backend(MVCComponent):
    """
    Abstract base class for all configuration backends. If you want to define
    your own backend, inherit from this class and implement all methods and
    members.

    :param backref: Backref to the :class:`gpyconf.Configuration` instance

    The :signal:`saved` signal is emitted when the backend is finished with
    saving; the :signal:`read` signal is emitted when the backend is finished
    with reading them ("read" is past here).
    """
    #: :const:`True` if this backend should run in compatibility mode
    #: (defaults to :const:`False`).
    compatibility_mode = False

    __events__ = ('saved', 'read')

    def __init__(self, backref):
        MVCComponent.__init__(self)
        self.backref = backref

    def read(self):
        """ Reads the configuration from the storage (file, database, ...) """
        raise NotImplementedError()

    def save(self):
        """ Saves the configuration to the storage """
        raise NotImplementedError()

    def set_option(self, name, value):
        """
        Sets option ``name`` to ``value``.
        """
        raise NotImplementedError()

    def get_option(self, option, default=NONE):
        """
        Returns the value of ``option``.
        If ``option`` doesn't exist, returns ``default`` if set
        else raises :exc:`MissingOption`.
        """
        raise NotImplementedError()

    def reset_all(self):
        """
        Resets all options.
        """
        # This can be done e.g. by deleting the storage file.
        raise NotImplementedError()

    @property
    def options(self):
        """
        A list of all options identifiers.
        """
        # (Could be implemented using a simple attribute, too)
        raise NotImplementedError()

    @property
    def tree(self):
        """
        A configuration tree like this::

            {
                'option1' : 'myvalue1', 'option2' : 'myvalue2',
                'option3' : 3, 'option4' : {'mykey' : 'myvalue'}
            }

        (Using standard methods, subclasses don't have to override
        this property)
        """
        return dict(izip(self.options, map(self.get_option, self.options)))
