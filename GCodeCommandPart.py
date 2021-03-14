#!/usr/bin/env python
# Processed by pycodetool https://github.com/poikilos/pycodetool
# 2021-03-13 21:54:12
# from System import *
# from System.Collections.Generic import *
# from System.IO import *
# from System.Text import *

import sys


class GCodeCommandPart:
    def __init__(self):
        # TODO: Make _Type, _Character, _Number, and _Text public (no _)
        self._Type = None
        self._Character = None
        self._Number = None
        self._Text = None

    def ToString(self):
        if self._Type == GCodeCommandPartType.Space:
            return SpaceString.OfLength(self._Number)
        elif self._Type == GCodeCommandPartType.CharacterAndNumber:
            return self._Character + str(self._Number)
        elif self._Type == GCodeCommandPartType.Comment:
            return ';' + self._Text
        elif self._Type == GCodeCommandPartType.Text:
            return self._Text
        else:
            raise Exception("Internal error")

    def WriteTo(self, writer):
        if self._Type == GCodeCommandPartType.Space:
            writer.write(SpaceString.OfLength(self._Number))
        elif self._Type == GCodeCommandPartType.CharacterAndNumber:
            writer.write(self._Character)
            writer.write(self._Number.ToString("##0.#####"))
        elif self._Type == GCodeCommandPartType.Comment:
            writer.write(';')
            writer.write(self._Text)
        else:
            raise Exception("Internal error")

    @classmethod
    def ParseStringToParts(cls, line):
        isFirstPart = True
        index = 0
        while index < line.Length:
            if line[index] == ';':
                pass
            if Char.IsWhiteSpace(line[index]):
                count = 1
                index += 1
                while (index < line.Length) and Char.IsWhiteSpace(line, index):
                    count += 1
                    index += 1
            else:
                part = GCodeCommandPart()
                part.Type = GCodeCommandPartType.CharacterAndNumber
                part.Character = line[index]
                index += 1
                numberStart = index
                while ((index < line.Length)
                       and not Char.IsWhiteSpace(line, index)):
                    index += 1
                part.Number = Decimal.Parse(
                    line.Substring(numberStart, index - numberStart)
                )
                wasFirstPart = isFirstPart
                isFirstPart = False
                if (wasFirstPart and (part.Character == 'M')
                        and ((part.Number == 117m)
                             or (part.Number == 118m))
                        and (index < line.Length)):
                    # Return remainder of line as a single text block
                    count = 1
                    index += 1
                    while ((index < line.Length)
                            and Char.IsWhiteSpace(line, index)):
                        count += 1
                        index += 1
                    if index < line.Length:
