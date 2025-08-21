import functools
from ..exceptions import BNetRegionError


def sc2_region(func):

    @functools.wraps(func)
    def wrapper_sc2_region(*args, **kwargs):
        if args[0].lower() == 'cn':
            raise BNetRegionError("Not allowed in region")
        return func(*args, **kwargs)
    return wrapper_sc2_region


def sc2_cn_only(func):
    @functools.wraps(func)
    def wrapper_sc2_region(*args, **kwargs):
        if args[0].lower() != 'cn':
            raise BNetRegionError("Not allowed in region")
        return func(*args, **kwargs)
    return wrapper_sc2_region
