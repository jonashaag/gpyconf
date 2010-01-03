Usage Guide
===========
In the following I will explain how to use gpyconf within your application.
I will go into detail about how to basically use the framework, talk about
the API, tell you how to change the used backend or frontend, explain how
to use signals and so on. If you're in a hurry, you're better off with the
:doc:`Quickstart manual <quickstart>`, because things will probably go
into detail here and you might not be interested in them.


Thinking about your configuration model
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The first step when you start using gpyconf with your application is to
think about *what you actually need*. Sure, you want your configuration
handled, but before you can start off you need to think about what you
want to store. Say you've written an amazing OGG audio player software and
you want your users to be able to customize the player's behaviour and
style. Let's keep it simple; you'll offer these three options:

1. Crossfading time --- Let the user set the time in seconds your player will
   use to cross-fade the next song
2. Show album art --- Let the user enable or disable the display of album
   covers within the player
3. Skin --- Let the user chose between some skins delivered with the player to
   customize the player's appearance

So you've thought of what you need to store, next step will be to think of
*how* you would like to store this. Using gpyconf, every configuration
option has to have a datatype, so let's work them out:

1. Crossfading time --- an integer between 0 (disabled) and 30 seconds should be nice
2. Show album art --- classical boolean option (there's only
   *"Yes, I wan't to have this"* and *"No, I don't want to have this"*)
3. Skin --- A string name chosen from a list of available values (skins)


Defining the configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~
The next step is to turn that model idea into code. Let's take the example
worked out above and write it down::

    import gypconf

    class MyAudioPlayerConfiguration(gpyconf.Configuration):
        crossfading_time = gpyconf.fields.IntegerField('Crossfading time', min=0, max=30)
        show_album_art = gpyconf.fields.BooleanField('Show album art', default=True)
        skin = gpyconf.fields.MultiOptionField('Skin', options=(
            ('default', 'Ugly default skin'),
            ('jukebox', 'Jukebox'),
            ('girlish', 'Girlish')))

Regarding this code example you can easy see that:

1. Every configuration is defined in form of a class derived from the
   :class:`Configuration <gpyconf.gpyconf.Configuration>` class
2. Your configuration model is defined in so-called fields
3. These fields are defined as class attributes
4. These fields can have a label ("Crossfading time", "Skin")
5. These fields can have a default value (``default=True``)
6. These fields can be called with additional options like ``min=X``, depending
   on the field.

That's the basics about how to turn out your theoretical option model into
working Python code.


The API or: Using that configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
As you know, classes are just kinda prototypes (at least in Python they
are), and because "gpyconf configuration classes" aren't anything special,
they are prototypes, too. Therefore, if you want to use the configuration,
you musn't keep it as prototype but you need to instantiate it::

    configuration = MyAudioPlayerConfiguration()

This constructor call loads the :doc:`Backend <mvc/backends>` and reads
stored values if available. As next step, you might not only want to
*define* options, but you possibly might want to *use* (read, change and
write) them, too.

gpyconf offers a very, very, very simple API for using the option values:
Just use them like they were normal attributes. If your option was named
``foo``, you access that option using ``configuration_instance.foo``. In
our example, we would get the value of the ``crossfading_time`` using ::

    >>> configuration.crossfading_time
    0

And the same way, we would set that option value::

    configuration.crossfading_time = 2 # seconds

Regarding the first attribute access you might be confused: Didn't we set
the :attr:`crossfading_time` attribute to something with ``IntegerField(...)``,
so it should return something like ``<IntegerField object at memaddress>``?
You're perfectly right, it should! This is the only "magic" thing you have
to keep in mind:

.. note::
   Accessing a configuration classes' attribute previously defined as field
   does not return the field instance itself, but **it's value**.

This is very important to remember, so put that in your pipe and smoke it!

You can still access the field instances using the
:attr:`fields <gpyconf.gpyconf.Configuration.fields>` attribute ::

    >>> configuration.fields['crossfading_time']
    <gpyconf.fields.fields.IntegerField object at 0xfoobar>
    >>> configuration.fields.crossfading_time # this is exactly the same
    <gpyconf.fields.fields.IntegerField object at 0xfoobar>

but you probably won't need that.

A short interactive python console log follows to clarify how that API works::

    >>> configuration = MyAudioPlayerConfiguration()    # 1
    >>> configuration.crossfading_time                  # 2
    0
    >>> configuration.crossfading_time = 5              # 3
    >>> configuration.crossfading_time                  # 4
    5
    >>> configuration.fields.crossfading_time           # 5
    <gpyconf.fields.fields.IntegerField object at 0xb789f2ac>
    >>> configuration.fields.crossfading_time.value     # 6
    5
    >>> configuration.crossfading_time = 10 # 7
    >>> configuration.fields.crossfading_time.value     # 8
    10
    >>> configuration.skin                              # 9
    'default'
    >>> configuration.skin = 'jukebox'                  # 10
    >>> configuration.skin                              # 11
    'jukebox'

Compare the output of statement #4 and #6 and you will recognize that
``configuration_instance.foo`` is exactly the same as
``configuration_instance.fields.foo.value``, so everytime when you access
an option using the API you'll get or change the field's
:attr:`value <gpyconf.fields.base.Field.value>` attribute.


Value validation
~~~~~~~~~~~~~~~~
To protect fields from invalid input, almost every field is limited to values
of a specific scheme. For example, the
:class:`IntegerField <gpyconf.fields.fields.IntegerField>` does only allow
integer values (or any values compatible to integers, for example, strings
counting only numerics and so on). Congruently, the
:class:`BooleanField <gpyconf.fields.fields.BooleanField>` does only allow
boolean values, the :class:`ColorField <gpyconf.fields.fields.ColorField>`
allows only colors (RGB tuples or hexadecimal numbers) and so on.

Those validation checks are not runned at "run time" but when you want to
save the configuration. This guarantees that no invalid values are stored.

Although those checks are automatically runned when trying to save the
configuration, you might want to check at "run time" wether the current
fields' value is valid or not. You can do this using the :meth:`isvalid
<gpyconf.fields.base.Field.isvalid>` method::

    >>> configuration.crossfading_time = 5
    >>> configuration.fields.crossfading_time.isvalid()
    True
    >>> configuration.crossfading_time = 100
    >>> configuration.fields.crossfading_time.isvalid()
    False
    # We set the maximum allowed value to 30, so 100 is invalid in this case

Please note that validation checks are somewhat different from datatype
conversions. Mostly all fields run datatype conversions on values before
they "accept" them to ensure that you'll get back the datatype you expect.
For example, the :class:`IntegerField <gpyconf.fields.fields.IntegerField>`
tries to convert all values to the  :class:`int` datatype. See this example::

    >>> configuration.crossfading_time = '42'
    >>> configuration.crossfading_time
    42
    >>> type(configuration.crossfading_time)
    <type 'int'>

Naturally, not every "value" (Python object) is compatible to the
:class:`int` datatype. gpyconf raises an error if we want to set
completely invalid datatypes::

    >>> configuration.crossfading_time = 'this.is.not.an.integer'
    InvalidOptionError    Traceback (most recent call last)
    ....
    InvalidOptionError: 'IntegerField allows only int or float types between 0
    and 30, stepped with 1, not str'

.. warning::
   There's a huge difference between datatype conversions the fields do every
   time you update their value and *real* validation checks!
   While converting between datatypes only very basic and stupid validation is
   done. For example, if you set an maxmimum value for an
   :class:`IntegerField <gpyconf.fields.fields.IntegerField>`, this is ignored
   completely while converting to :class:`int`. To be sure that a value is a
   valid one for the field with it's current settings, you should *always*
   ask the :meth:`isvalid <gpyconf.fields.base.Field.isvalid>` method!


Switching the frontend or backend
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Thanks to gpyconf's modular architecture you can switch the frontend and/or
backend components like you want to and completely independently. To do so,
simply overwrite the :attr:`backend <gpyconf.gpyconf.Configuration.backend>`
and/or :attr:`frontend <gpyconf.gpyconf.Configuration.frontend>` attributes::

    import gpyconf
    import gpyconf.backends.json

    class MyConfiguration(gpyconf.Configuration):
        backend = gpyconf.backends.json.JSONBackend
        ...

or ::

    import gpyconf
    import yourmegalcoolfrontend

    class MyConfiguration(gpyconf.Configuration):
        frontend = yourmegalcoolfrontend.Frontend
        ...

you can also change that components at class instantiation time::

    MyConfiguration(frontend=YourOtherCoolFrontend)


Passing arguments to those components works, too. For example if your want
to pass the ``title`` option to the default GTK+ frontend, call it with
the :meth:`with_arguments <mvc.MVCComponent.with_arguments>` option::

    class MyConfiguration(gpyconf.Configuration):
        frontend = gpyconf.frontends._gtk.GtkConfigurationWindow.with_arguments(
            title='Hello World')
