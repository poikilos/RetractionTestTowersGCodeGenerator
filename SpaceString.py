#!/usr/bin/env python
# Processed by pycodetool https://github.com/poikilos/pycodetool
# 2021-03-13 21:54:12
# from System.Collections.Generic import *

import sys


class SpaceString:
    '''
    This is not necessary since Python has better ways of doing this
    (' ' * length).
    This is kept only for type checking purposes.
    '''
    _s_cache = {}

    def __init__(self):
        pass

    @classmethod
    def _cache(cls, length):
        if not isinstance(length, int):
            raise ValueError("The length must be an int but"
                             " is \"{}\".".format(length))
        newStr = ' ' * length
        cls._s_cache[str(length)] = newStr
        return newStr

    @classmethod
    def OfLength(cls, length):
        return cls._s_cache.get(str(length)) or cls._cache(length)
