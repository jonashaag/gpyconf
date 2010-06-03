# %FILEHEADER%

from . import events

class MVCComponent(events.GSignals):
    """
    Base class for all MVC components (frontend, backend, controller).
    Implements the :class:`gpyconf.events.GSignals` class, so signal emitting
    and connecting can be used for inheriting classes.
    """
    def __init__(self):
        events.GSignals.__init__(self)
        self.add_event('log')

    def log(self, message, level='debug'):
        self.emit('log', message, level=level)

    def warn(self, message):
        self.log(message, 'warning')

    @classmethod
    def with_arguments(cls, *args, **kwargs):
        """
        Returns a :class:`ComponentFactory` instance. That factory is a wrapper
        to this class that returns an instance of this class when calling it
        passing ``args`` and ``kwargs`` as additional arguments. For example, ::

            wrapper = MyMVCComponentSubclass.with_arguments(42, foo='bar')
            wrapper(a, b)

        is equal to ::

            MyMVCComponentSubclass(a, b, 42, foo='bar')
        """
        return ComponentFactory(cls, *args, **kwargs)

    @property
    def _class_name(self):
        """ Wrapper to :attr:`self.__class__.__name__` """
        return self.__class__.__name__

class ComponentFactory(object):
    def __init__(self, cls, *args, **kwargs):
        self.cls = cls
        self.args = args
        self.kwargs = kwargs

        self.__name__ = cls.__name__
        self.__module__ = cls.__module__
        self.__doc__ = cls.__doc__


    def __call__(self, *args):
        return self.cls(*args+self.args, **self.kwargs)

    def __repr__(self):
        return "<ComponentFactory wrapper to '%s'>" % self.cls.__name__
