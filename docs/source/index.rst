gpyconf documentation
=====================

Table of Contents
-----------------

.. toctree::
   :maxdepth: 3

   quickstart
   usage
   architecture
   mvc
   signals
   fields
   own
   stuff


about gpyconf
-------------

gpyconf is a configuration framework based on gtk. With gpyconf, you can have
configuration handling for your Python application within seconds, including
different ways to store that configuration options (:doc:`Backends <mvc/backends>`)
and a pretty, auto-generated (of course, :doc:`replaceable <mvc/frontends>`)
preferences dialog. gpyconf's models and model definitions are inspired by
`django <http://djangoproject.com>`_'s, therefore, gpyconf follows the commonly
used and time-tested `Model-View-Controller (MVC) <http://en.wikipedia.org/wiki/MVC>`_
pattern.

If you're impatient and/or want to see results quickly, go on reading the
:doc:`quickstart` and :doc:`usage` pages.

The :doc:`architecture` section gives you information on gpyconf's underlying
MVC architecture theory.

The :doc:`mvc` section gives you detailed information about each of the
three MVC components and contains API documentation so you will be able
to implement your own Model or View (or Controller).

The last (but not least important) section tells you how to
:doc:`install <stuff/installation>` and run gpyconf on your machine.


Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

