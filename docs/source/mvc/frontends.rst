Frontends --- Interface to the user
===================================

What is a frontend?
~~~~~~~~~~~~~~~~~~~
...

Typically, frontends are configuration dialogs your users can interact with,
but nobody bars you from using a web interface or your
`coffee maker <http://tldp.org/HOWTO/Coffee.html>`_ as frontend.

In your :doc:`Configuration definition </usage>`, you can overwrite the
default frontend (which is a
:class:`GtkConfigurationWindow <gpyconf.frontends.gtk.ConfigurationDialog>`)
using the :attr:`frontend` attribute. Example::

    class MyConfiguration(Configuration):
        frontend = YourCrazyWebInterface

This tells the Controller to use the :class:`YourCrazyWebInterface` class.

See see that you can define and use your very own frontends. To do so,
simply define a class inheriting from :class:`Frontend` and implement all
methods. See :doc:`/own` for more information about using self-built
frontends.


Included frontends
~~~~~~~~~~~~~~~~~~
.. toctree ::
   :maxdepth: 1

   GTK+ Frontend (default) <frontends/gtk>


API documentation
~~~~~~~~~~~~~~~~~
.. automodule:: gpyconf.frontends
   :members:
   :undoc-members:
