from deprecated.classic import ClassicAdapter
from deprecated import deprecated
from typing import Callable, Dict, Any
import functools
import warnings


class ClassicAdapterNoDefaultMessage(ClassicAdapter):
    def get_deprecated_msg(self, *args, **kwargs):
        return self.reason



def renamed_function( fun, old_name="" ):
    """Copy the function and emit a deprecation warning

    Parameters
    ----------
    fun : fun
        The new function
    old_name : str, optional
        The name of the old function. The default is "".

    Returns
    -------
    fun
        The decorated function

    Example
    -------
    >>> test_old = renamed_function(test_new, "test_old")
    >>> test_old()
    DeprecationWarning: test_old has been renamed test_new
    """
    return deprecated( fun, reason = f"{old_name:} has been renamed {fun.__name__:}" , adapter_cls = ClassicAdapterNoDefaultMessage)


def moved_function( fun, old_name="", new_location=None ):
    """Copy the function and emit a deprecation warning

    Parameters
    ----------
    fun : fun
        The new function
    old_name : str, optional
        The name of the old function. The default is "".
    new_location : str, optional
        The location of the new function. The default is r"{fun.__module__:}.{fun.__name__:}".

    Returns
    -------
    fun
        The decorated function

    Example
    -------
    >>> test_old = moved_function(test_new, "test_old")
    >>> test_old()
    DeprecationWarning: test_old has been has been moved to ...
    """
    
    if new_location is None : 
        new_location = r"{fun.__module__:}.{fun.__name__:}"
    return deprecated( fun, reason = f"{old_name:} has been moved to {new_location:}" , adapter_cls = ClassicAdapterNoDefaultMessage)




# Code from https://stackoverflow.com/questions/49802412/how-to-implement-deprecation-in-python-with-argument-alias
def deprecated_alias(**aliases: str) -> Callable:
    """Decorator for deprecated function and method arguments.

    Example
    -------
    >>> @deprecated_alias(old_arg='new_arg')
    >>> def myfunc(new_arg):
    >>>    ...

    """

    def deco(f: Callable):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            rename_kwargs(f.__name__, kwargs, aliases)
            return f(*args, **kwargs)

        return wrapper

    return deco


def rename_kwargs(func_name: str, kwargs: Dict[str, Any], aliases: Dict[str, str]):
    """Helper function for deprecating function arguments."""
    for alias, new in aliases.items():
        if alias in kwargs:
            if new in kwargs:
                raise TypeError(
                    f"{func_name} received both {alias} and {new} as arguments!"
                    f" {alias} is deprecated, use {new} instead."
                )
            warnings.warn(
                message=(
                    f"`{alias}` is deprecated as an argument to `{func_name}`; use"
                    f" `{new}` instead."
                ),
                category=DeprecationWarning,
                stacklevel=3,
            )
            kwargs[new] = kwargs.pop(alias)



# Code from https://stackoverflow.com/questions/9008444/how-to-warn-about-class-name-deprecation
class DeprecatedClassMeta(type):
    """

    Example
    -------
    >>> class OldClass(metaclass=DeprecatedClassMeta):
    >>>    alias = NewClass
    """

    def __new__(cls, name, bases, classdict, *args, **kwargs):

        alias = classdict.get('alias')

        def new(cls, *args, **kwargs):
            alias = getattr(cls, 'alias')

            if alias is not None:
                warnings.warn("{} has been renamed to {}, the alias will be "
                     "removed in the future".format(cls.__name__,
                         alias.__name__), DeprecationWarning, stacklevel=2)

            return alias(*args, **kwargs)

        classdict['__new__'] = new

        fixed_bases = []

        for b in bases:
            alias = getattr(b, 'alias', None)

            if alias is not None:
                warnings.warn("{} has been renamed to {}, the alias will be "
                     "removed in the future".format(b.__name__,
                         alias.__name__), DeprecationWarning, stacklevel=2)

            # Avoid duplicate base classes.
            b = alias or b
            if b not in fixed_bases:
                fixed_bases.append(b)

        fixed_bases = tuple(fixed_bases)

        return super().__new__(cls, name, fixed_bases, classdict,
                               *args, **kwargs)

    def __instancecheck__(cls, instance):
        return any(cls.__subclasscheck__(c)
            for c in {type(instance), instance.__class__})

    def __subclasscheck__(cls, subclass):
        if subclass is cls:
            return True
        else:
            return issubclass(subclass, getattr(cls,
                              'alias'))


def renamed_class( NewClass, old_name ):
    """Copy the class and emit a deprecation warning.

    Parameters
    ----------
    NewClass : class
        The new class
    old_name : str, optional
        The name of the old class.

    Returns
    -------
    Class
        The decorated class

    Example
    -------
    >>> TestOld = renamed_class(TestNew, "TestOld")
    >>> TestOld()
    DeprecationWarning: TestOld has been renamed TestNew
    """

    class OldClass_(metaclass=DeprecatedClassMeta):
        alias = NewClass
    OldClass_.__name__ = old_name
    return OldClass_







