Coding Guidlines
================

When contributing code to gpyconf or submitting your backends or frontends,
your code should fit into this guidlines.


Basic coding style
~~~~~~~~~~~~~~~~~~
1. Follow :pep:`8`.
2. Use relative imports whereever you can. See "Relative imports" subsection.
3. Do *NOT* mix GUI logic with program logic, use :doc:`signals </signals>` to
   connect those two components.
4. Use pseudo-constants instead of hardcoding fix values defined at compile time.


Relative Imports
~~~~~~~~~~~~~~~~
It is absolutely essential that your code uses relative imports wherever it
is possible. Do not use ::

    from gpyconf.fields import Field

when you're developing a gpyconf compontents, use imports like ::

    from ..fields import Field

Furthermore, use relative imports for importing modules that live in the same
directory namespace. If your directory tree looks like this ::

    mymodule
        __init__.py
        foo.py
        bar.py

and you want to import stuff from `foo.py` in `bar.py`, use ::

    from .foo import yourstuff

or ::

    from . import foo

If you want to import stuff defined in the `__init__.py` file, import it with ::

    from . import yourotherstuff


Whitespace usage
~~~~~~~~~~~~~~~~
As defined in PEP8, use whitespace to separate

* operators (``1 + 2``, not ``1+2``)
* variable names and variable values (``a = b``, not ``a=b``)
* arguments (``42, foo=bar``, not ``42,foo=bar``)

Furthermore,

* between class definitions, put two empty lines
  (if they belong together logically, put only one line)
* don't put any empty lines between class headers, their docstrings and the
  first class member
* use empty lines (sparingly!) to separate code logically
