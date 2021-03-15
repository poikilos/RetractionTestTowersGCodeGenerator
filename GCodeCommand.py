﻿#!/usr/bin/env python
# Processed by pycodetool https://github.com/poikilos/pycodetool
# 2021-03-13 21:54:12
# from System import *
# from System.IO import *
# from System.Linq import *
# from System.Text import *

import sys

from GCodeCommandPart import (
    GCodeCommandPart,
)

from GCodeCommandPartType import GCodeCommandPartType
from CommandCache import CommandCache


class GCodeCommand:
    def __init__(self, line):
        self._line = line  # for debugging only
        self.Command = None
        self.CommandType = None
        self.CommandNumber = None
        self._parts = list(GCodeCommandPart.ParseStringToParts(line))
        # print("line: `{}`".format(line))
        # print("  parts: {}".format(self._parts))
        firstPart = None

        for part in self._parts:
            if part.Type == GCodeCommandPartType.CharacterAndNumber:
                if firstPart is None:
                    firstPart = part
                # break
                else:
                    if isinstance(part.Number, int):
                        # if part.Character in GCodeCommandPart.F_PARAMS
                        part.Number = float(part.Number)

        if firstPart is not None:
            self.CommandType = firstPart.Character
            self.CommandNumber = int(firstPart.Number)
            try:
                self.Command = CommandCache.Get(self.CommandType,
                                                self.CommandNumber)
            except Exception as e:
                print("line: `{}`".format(line))
                print("  parts: {}".format(self._parts))
                raise e
        else:
            pass
            # if line[0:1] != ";":
            #     print("WARNING: There is no firstPart in `{}`"
            #           "".format(line))

    def ToString(self):
        result = ""
        for part in self._parts:
            result += str(part)
        return result

    def WriteTo(self, writer):
        for part in self._parts:
            writer.write(part)

    def HasParameter(self, v):
        return self.GetPartByCharacter(v) is not None\

    def GetParameter(self, param):
        part = self.GetPartByCharacter(param)
        if part is None:
            print("line: `{}`".format(self._line))
            print("  parts: {}".format(self._parts))
            raise Exception("Command does not have a parameter '{}'"
                            "".format(param))

        return part.Number


    def SetParameter(self, param, value):
        part = self.GetPartByCharacter(param)
        if part is None:
            raise Exception("Command does not have a parameter '{}'"
                            "".format(param))
        part.Number = value

    def GetPartByCharacter(self, param):
        if len(param) != 1:
            raise ValueError("The param must be a character but is"
                             " \"{}\".".format(param))
        for part in self._parts:
            if ((part.Type == GCodeCommandPartType.CharacterAndNumber)
                    and (part.Character == param)):
                return part
        return None
