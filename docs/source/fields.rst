Configuration option Fields
===========================

Fields are -- at least for developers that *use* gpyconf, not develop costum
stuff for it -- the main thing you will work with. A field represents a
configuration option. Every configuration option has at least

* a type (representing a python datatype like :class:`str`, :class:`int`,
  :class:`list`) and
* a name for internal use

Furthermore, a field represents a frontend *widget*
(:abbr:`GUI (Graphical User Interface)` representation of a field).

To get more information on about how to use fields, please refer to the
:doc:`quickstart` section or, for detailed instructions, see the :doc:`usage`
manual.

API documentation for the :class:`Field` class and a list of all fields
follows.


The :class:`Field` base class
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. autoclass:: gpyconf.fields.base.Field
   :members:
   :exclude-members: get_value, set_value, validation_error, setfromconf,
                     on_initialized


Included fields
~~~~~~~~~~~~~~~
.. automodule:: gpyconf.fields.fields
   :members:
