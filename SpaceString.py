#!/usr/bin/env python
# Processed by pycodetool https://github.com/poikilos/pycodetool
# 2021-03-13 21:54:12
# from System.Collections.Generic import *

import sys


class SpaceString:
    def __init__(self):
        self._s_cache = Dictionary[int, str]()

    @classmethod
    def OfLength(cls, length):
        if self._s_cache.TryGetValue(length, ):
            cachedValue
        return self._s_cache[length] = System.String(' ', length)
