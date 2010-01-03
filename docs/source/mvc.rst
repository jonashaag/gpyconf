Components
==========
All three MVC components inherit from the :class:`mvc.MVCComponent` class which
adds the following features to them:

1. **Signal-emitting and connecting:** Implements the :class:`gpyconf.events.GSignals`
   class. You can use the :meth:`emit <gpyconf.events.GSignals.emit>` method to emit
   signals defined in :attr:`__events__ <gpyconf.events.GSignals.__events__>`. To that
   signals can be connected using the :meth:`connect <gpyconf.events.GSignals.connect>`
   method. For more about this, see the :doc:`signals` section.

2. **Factory wrappers**: Using the :meth:`with_arguments <mvc.MVComponent.with_arguments>`
   classmethod, you can create a wrapper to this class which takes additional
   arguments. When that wrapper is called, these additional arguments are added
   to the arguments scope. For more about this, see this method's documentation.

   *Whenever* you want to pass additional arguments to a frontend or backend,
   use this classmethod instead of instantiating that class directly,
   because gpyconf expects the frontend and backend classes to be callable
   (hence, it does not expect *instances*, but *classes*). Example::

       class MyConfiguration(gpyconf.Configuration):
           backend = ConfigParserBackend.with_arguments(filename='myconf.ini')


Components base class
~~~~~~~~~~~~~~~~~~~~~
.. autoclass:: gpyconf.mvc.MVCComponent
   :members:


The three components
~~~~~~~~~~~~~~~~~~~~
.. toctree::

    mvc/backends
    mvc/frontends
    mvc/configuration
