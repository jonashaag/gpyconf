Logging
=======
gpyconf uses logging all around; the logging output is printed to ``stdout``.

By default, the logging level is set to `warning`, which only shows warnings
and errors. You may redefine that level in your configuration definition using
the :attr:`logging_level` attribute. You can choose between the following
levels:

+-----------+--------------------------------------------------------------+
|   Level   | Description                                                  |
+===========+==============================================================+
| `error`   | Shows only errors                                            |
+-----------+--------------------------------------------------------------+
| `warning` | Shows errors and warnings                                    |
+-----------+--------------------------------------------------------------+
| `debug`   | Shows errors, warnings and debug messages                    |
+-----------+--------------------------------------------------------------+
| `info`    | Shows everything (errors, warnings, debug and info messages) |
+-----------+--------------------------------------------------------------+


This example shows how to set your debug level to `debug`::

    class MyConfiguration(Configuration):
        logging_level = 'debug'
