# coding: utf-8
# %FILEHEADER%

from ..fields import Field
from ..mvc import MVCComponent, ComponentFactory

class Frontend(MVCComponent):
    """
    Abstract base class for all frontends. If you want to define your own
    frontend, inherit from this class and implement all methods and members.

    The frontend is called with two parameters:

    :param backref:
        A :class:`weakref.ref` to the :class:`gypconf.Configuration` instance
    :param fields:
        The Model fields

    The frontend class now has to care about mapping those abstract fields
    to widgets. After adding a field to the display area (e.g. a window or
    a HTML page), it should emit the :signal:`add-field` signal.
    Furthermore, the frontend has to notify the Controller class about
    *every* value-change of *any* widget; whenever a widget value was
    changed, the :signal:`field-value-changed` signal should be emitted
    (passing the field as first and the new value as second parameter) --
    otherwise, the Controller class doesn't know about this value-change
    and thus, the changes will not be saved.

    """

    __events__ = (
        'add-field',
        'close',
        'closed',
        'save',
        'field-value-changed',
        'log'
    )

    def __init__(self):
        MVCComponent.__init__(self)

    def run(self):
        """ Run the frontend ;-) """
        raise NotImplementedError()

    def close(self):
        """
        Manages the close event of the frontend.
        If all inputs are valid, stops the frontend (e.g. closes the window).
        (If not, it adds an error message using :meth:`add_value_error`.)

        This method emits the following singals:

        +-----------------------+--------------------------------------------------------------+
        |        Signal         |                  Description                                 |
        +=======================+==============================================================+
        | :signal:`save`        |                                                              |
        |                       |                                                              |
        |                       | When this signal is emitted, the                             |
        |                       | Controller class saves the current field                     |
        |                       | values. If one of that value is not valid, an                |
        |                       | :exc:`InvalidOptionError <gpyconf.exceptions.InvalidOption>` |
        |                       | is risen. This error should be  catched and                  |
        |                       | the user should then be  notified about that                 |
        |                       | incorrect input to make him correct that fault.              |
        +-----------------------+--------------------------------------------------------------+
        | :signal:`close`       | Emitted before the frontend is closed                        |
        +-----------------------+--------------------------------------------------------------+
        | :signal:`closed`      | Emitted after the frontend is closed                         |
        +-----------------------+--------------------------------------------------------------+
        """
        self.emit('close')
        raise NotImplementedError()
        self.emit('closed')
