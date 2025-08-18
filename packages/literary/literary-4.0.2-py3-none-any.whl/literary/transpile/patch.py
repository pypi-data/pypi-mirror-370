""""""
from typing import Callable, Type, TypeVar
T = TypeVar('T')
WRAPPER_NAMES = ('fget', 'fset', 'fdel', '__func__', 'func')

def patch(cls: Type) -> Callable[[T], T]:
    """Decorator to monkey-patch additional methods to a class.

    At import-time, this will disappear and the source code itself will be transformed
    Inside notebooks, the implementation below will be used.

    :param cls:
    :return:
    """

    def get_name(func):
        try:
            return func.__name__
        except AttributeError:
            for attr in WRAPPER_NAMES:
                try:
                    return getattr(func, attr).__name__
                except AttributeError:
                    continue
            raise

    def _notebook_patch_impl(func):
        setattr(cls, get_name(func), func)
        return func
    return _notebook_patch_impl