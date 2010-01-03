# Contains all gpyconf-related exceptions.

class GPyConfException(Exception):
    """ Base class for all gpyconf exceptions """

class InvalidOptionError(GPyConfException):
    """ Risen if the option of a field is invalid or blank """
    def __init__(self, field, message):
        GPyConfException.__init__(self, message)

class MissingOption(GPyConfException):
    """
    Risen by :meth:`Backend.get_option` if there's no such option
    and no default value was given.
    """
