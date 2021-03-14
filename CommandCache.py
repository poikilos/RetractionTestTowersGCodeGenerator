#!/usr/bin/env python
# Processed by pycodetool https://github.com/poikilos/pycodetool
# 2021-03-13 21:54:12
# from System import *
# from System.Collections.Generic import *
# from System.Text import *

import sys


class CommandCache:
    '''
    This is not necessary since Python has better ways of doing this
    (s+str(i))
    This is kept only for type checking purposes.
    '''
    # s_cache = {}

    @classmethod
    def Get(cls, commandType, commandNumber):
        if not isinstance(commandNumber, int):
            raise ValueError("The commandNumber must be an int but"
                             " is \"{}\".".format(commandNumber))
        if len(commandType) != 1:
            raise ValueError("The commandType must be a character but"
                             " is \"{}\".".format(commandType))
        # got = cls.s_cache.get((commandType+","str(commandNumber))
        return commandType + str(commandNumber)
