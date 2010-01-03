Signals and Events --- The glue
===============================

Some theory (yes, again)
~~~~~~~~~~~~~~~~~~~~~~~~
As told before, the three MVC components (the Model, the View and the Controller)
can live for their own independently of both of the others.
*But wait -- if they are independent, they cannot know of each other!*
Yes, that's true -- none of the three components knows of each other,
but there's a way they communicate: Signals.

Each component "emits" signals at specific points in the code, for example,
the :signal:`field-value-changed` signal (which is emitted by the Controller
class) is emitted when a field changed it's value.

The Controller class connects to signals the backend and the frontend emit;
it kinda establishes a connection between them ("routing" over the Controller
class).

The event system gpyconf uses is compatible to the GObject/GSignals system.
I decided to make the event system compatible to that API because frontends
will mostly be written using GTK (which uses the GObject GSignals system) but
it wouldn't be straightforward to make gpyconf dependent on that library.


Connect to signals
~~~~~~~~~~~~~~~~~~
Of course, not only those three components can connect to each other, your
application code, can do so, too. Do this by ::

    component.connect(your_signal, your_callback)

Whenever ``your_signal`` is emitted, ``your_callback`` is called with
the sender class as first argument and the arguments passed to that
emit call. For example, we want to connect a callback to the
:signal:`field-value-changed` signal emitted by the Controller class. ::

    class MyConfiguration(Configuration):
        ...

    myconf = MyConfiguration()

    def my_callback(sender, infected_field, new_value):
        print "The Controller reported that %s changed its value to %s" % (
            infected_field, new_value)

    myconf.connect('field-value-changed', my_callback)

.. note::
   For a complete list of signals you can connect to, see the documentation
   for the :doc:`Configuration <mvc/configuration>`,
   :doc:`Frontend <mvc/frontends>` and :doc:`Backend <mvc/backends>` classes.


Emit signals
~~~~~~~~~~~~
If you want to use signals in your own classes (for example, if you're writing
your own backend or frontend or modifying some of them or just want to play
around), you have to inherit your class from the :class:`GSignals` class.
As told before, gpyconf's event system implements a GSignals-compatible API
(by offering the :meth:`emit <GSignals.emit>` and :meth:`connect <GSignals.connect>`
methods), so you can use your classes like they were inheriting from
:class:`gobject.GObject`.

Here's an example of how to emit signals::

    class MyGreatFrontend(Frontend):
        def __init__(self):
            Frontend.__init__(self)
            self.add_signal('my-great-signal')

        def emit_something(self):
            self.emit('my-great-signal', 42)

.. note::
   All signals you want to use in your classes have to be defined in the
   :attr:`__event__` list *before* initializing the :class:`GSignals` class.

.. warning::
   If you're inheriting from another class that defines that :attr:`__event__`
   list itself and you don't want to lose this list, you can add signals using
   the :meth:`add_signal <GSignals.add_signal>` and
   :meth:`add_signals <GSignals.add_signals>` methods belatedly.
   Remember that you (or any code you use, including gpyconf) can not connect
   to any signal before it was defined in the :attr:`__events__` list or added
   to that list using the named methods!


API documentation
~~~~~~~~~~~~~~~~~

.. autoclass:: gpyconf.events.GSignals
   :members:

.. autoclass:: gpyconf.events.GEventRegister

.. autoclass:: gpyconf.events.EventRegister
   :members:

.. autoclass:: gpyconf.events.InvalidEvent
