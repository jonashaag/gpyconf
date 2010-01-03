Installation
============

Currently, there aren't any public releases of gpyconf. Althought gpyconf is
developed rapidly and therefore it's likely to be very unstable most time,
there are some development snapshots provided that should be save to use.


Get the code...
~~~~~~~~~~~~~~~

Last stable version
--------------------
You can get the last stable (more precisely, *working*) copy of gpyconf with::

    hg clone http://bitbucket.org/Dauerbaustelle/gpyconf-stable

Bitbucket also provides archives that you can download if you're not familiar
with Mercurial:

* `gpyconf-stable as zip`_
* `gpyconf-stable as gz`_
* `gpyconf-stable as bz2`_

.. _gpyconf-stable as zip: http://bitbucket.org/Dauerbaustelle/gpyconf-stable/get/tip.zip
.. _gpyconf-stable as gz: http://bitbucket.org/Dauerbaustelle/gpyconf-stable/get/tip.gz
.. _gpyconf-stable as bz2: http://bitbucket.org/Dauerbaustelle/gpyconf-stable/get/tip.bz2


Development version
-------------------
That current development state can be downloaded with::

    hg clone http://bitbucket.org/Dauerbaustelle/gpyconf

.. warning::

   This version is *ONLY* for developers; do *NOT* try to use it in
   productive environment! The development version is very likely to be
   broken and may even destroy or corrupt data on your machine
   (where "data" covers [hopefully] only gpyconf-related data).

   Use one of the stable releases instead.


Old stable releases
-------------------
There aren't any old releases yet.


... and install it!
~~~~~~~~~~~~~~~~~~~
gpyconf uses `setuptools`_, you can install it like any other python package
using setuptools (the following command has to be executed as super user)::

    python setup.py install

.. _setuptools: http://pypi.python.org/pypi/setuptools
