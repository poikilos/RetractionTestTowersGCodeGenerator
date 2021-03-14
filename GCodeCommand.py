#!/usr/bin/env python
# Processed by pycodetool https://github.com/poikilos/pycodetool
# 2021-03-13 21:54:12
# from System import *
# from System.IO import *
# from System.Linq import *
# from System.Text import *

import sys


class GCodeCommand:

    def __init__(self, line):
        self._parts = GCodeCommandPart.ParseStringToParts(line).ToArray()
        firstPart = self._parts.FirstOrDefault()
        if firstPart is not None:
            self._CommandType = firstPart.Character
            self._CommandNumber = firstPart.Number
            self._Command = CommandCache.Get(self._CommandType,
                                             self._CommandNumber)

    def ToString(self):
        builder = StringBuilder()
        enumerator = self._parts.GetEnumerator()
        while enumerator.MoveNext():
            part = enumerator.Current
            builder.Append(part)
        return builder.ToString()

    def WriteTo(self, writer):
        enumerator = self._parts.GetEnumerator()
        while enumerator.MoveNext():
            part = enumerator.Current
            part.WriteTo(writer)

    def HasParameter(self, v):
        pass
