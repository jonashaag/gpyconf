Quickstart --- gpyconf in 3 minutes
===================================
For using gpyconf you do not need to know and understand the :doc:`MVC <mvc>`
pattern or anything of gpyconf's architecture, you can simply use it as it is.


Defining your Model
-------------------
Let's say you've written some amazing multi protocol instant messenger and you
want your users to enter the following information:

* :attr:`im_service` -- selection of three messaging protocols (*required*)
* :attr:`nickname` -- a :class:`string` (*required*)
* :attr:`password` -- a :class:`string` (*required*)
* :attr:`country` -- the country they live in (*optional*)

Well then, :doc:`install <stuff/installation>` gpyconf, create a new Python module
and fill it with the following code::

    import gpyconf

    class UserOptions(gpyconf.Configuration):
        im_service = gpyconf.fields.MultiOptionField('Service', options=(
            ('xmpp', 'Jabber/XMPP'),
            ('icq', 'ICQ'),
            ('msn', 'MSN')
        ))
        nickname = gpyconf.fields.CharField('Nickname', blank=False)
        password = gpyconf.fields.PasswordField('Password', blank=False)
        country = gpyconf.fields.MultiOptionField('I live in', options=(
            ('us', 'United States of America'),
            ('gb', 'Great Britian'),
            ('de', 'Germany'),
            ('at', 'Austria')
        ))

    useroptions = UserOptions()
    print useroptions.nickname
    # will print you an empty line on first start, then the name you stored
    print useroptions.country
    # will print you 'us' on first start, then the code of the country you chose
    useroptions.run_frontend()
    # show the window

If you know the `django webframework <http://djangoproject.com>`_, you're most
likely to notice the great similarity between gpyconf's and django's model
definitions. If you're not familiar with django or it's models, let me explain
how it works:

You can define fields in your :class:`gpyconf.Configuration` subclass
(in this case, it's named :class:`UserOptions`) that represent primitive or
non-primitive (Python) datatypes (like :class:`bool`, :class:`string`,
:class:`int`, but also stuff like tables and dropdowns (which may be used
as :class:`list`)).

.. note::
    The ``blank=True`` arguments passed to the :class:`CharFields <gpyconf.fields.CharField>`
    enforce that those fields musn't be empty ("blank") when saving the options.
    Most fields mustn't be blank by default, but for :class:`CharFields <gpyconf.fields.CharField>`
    you have to set this option manually ("empty strings are strings, too").

See :doc:`fields` for an overview of predefined fields. If you want to use your
very own fields, please refer to :doc:`own`.


Using the API
-------------
The API is very simple, but might be a little but confusing for newbies.
Regarding the print output, you probably have expected something like
"gpyconf.fields.<Some>Field instance at <SomeMemoryAddress>" to appear on the
screen, but both times you didn't get that stuff. It's because after
initialisation, accessing a field attribute doesn't return the field instance
itself, but **it's value**. You can still access that field via
``.fields.yourfield``, but you won't need this.

Regarding the API, after initialisation, ::

    myconfigurationinstance.fields.myfield.value

is the same as ::

    myconfigurationinstance.myfield


At this point you're almost done -- that's it! You can now take that stuff and
put it in your application. :doc:`Let me know <stuff/feedback>` if you succeeded!


Using Signals
-------------
Every component of the gpyconf framework (hence, the
:doc:`Backend <mvc/backends>`, the :doc:`Frontend <mvc/frontends>` and the
:doc:`Controller <mvc/configuration>`) supports and emits signals/events.
You can listen to that signals simply by connecting them to a function.
For more information about this, see :doc:`signals`.

Example::

    # ...
    def on_any_field_value_changed(sender_instance, field, new_value):
        print "Value of %s changed to %s" % (field.field_var, new_value)
    useroptions.connect('field-value-changed', on_any_field_value_changed)

This connects the :func:`on_any_field_value_changed` function the
'field-value-changed' signal, which is emitted when the user changed some value
using the frontend.

For a list of allowed events/signals for each component refer to their
documentation.
