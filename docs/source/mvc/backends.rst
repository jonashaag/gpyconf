Backends --- Interface to the storage
=====================================

What is a backend?
~~~~~~~~~~~~~~~~~~
...

In your :doc:`Configuration definition </usage>`, you can overwrite the default
backend (which is :class:`gpyconf.backends.configparser.ConfigParserBackend`)
using the :attr:`backend` attribute. Example::

    class MyConfiguration(Configuration):
        backend = backends.json.JSONBackend

This tells the Controller to use the :class:`JSONBackend`, which stores
options in a JSON file.

Of course you can define and use your very own backends. To do so, simply
define a class inheriting from :class:`Backend` and implement all methods.
See :doc:`/own` for more information about using self-built backends.

.. note::

    If your developing your own backend, you can choose it to run in
    "compatibility mode". In this mode, all values to store are converted
    to the :class:`unicode` datatype before calling the
    :meth:`set_option <Backend.set_option>` method. Similarly, they will
    be converted back to their original datatype when reading them.
    Although not using the compatiblity mode might have considerable
    advantages (database backends do lots of optimization on this score),
    using the compatiblity mode is much more  comfortable (because you do
    not have to care about datatypes) and  required by some backends that
    don't support other datatypes (e.g.  the default backend, the
    :class:`ConfigParserBackend <configparser.ConfigParserBackend>`).


Included backends
~~~~~~~~~~~~~~~~~
.. automodule:: gpyconf.backends.configparser
   :members:

.. automodule:: gpyconf.backends.json
   :members:


API documentation
~~~~~~~~~~~~~~~~~
.. automodule:: gpyconf.backends
   :members:
