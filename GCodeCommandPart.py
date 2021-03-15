#!/usr/bin/env python
# Processed by pycodetool https://github.com/poikilos/pycodetool
# 2021-03-13 21:54:12
# from System import *
# from System.Collections.Generic import *
# from System.IO import *
# from System.Text import *

from GCodeCommandPartType import GCodeCommandPartType
from SpaceString import SpaceString

import sys

from cc0code import (
    IsSpace,
    ToNumber,
)

class GCodeCommandPart:
    '''
    public members:
    Type -- a value that matches a constant from GCodeCommandPartType
    Character -- a G-code command character
    Number -- If Type is CharacterAndNumber, then Number is a param for
              the G-code command (which comes after the Character). If
              Type is Space, then it is the count of spaces. Otherwise
              it is None.
    Text -- additional text such as for when Type is
            GCodeCommandPartType.Comment
    '''
    def __init__(self, **kwargs):
        self.Type = kwargs.get("Type")
        self.Character = kwargs.get("Character")
        self.Number = kwargs.get("Number")
        self.Text = kwargs.get("Text")

    def __str__(self):
        return self.ToString()

    def __repr__(self):
        # This is used when a list containing this is formatted as text.
        return self.ToString()

    def ToString(self):
        if self.Type == GCodeCommandPartType.Space:
            return SpaceString.OfLength(self.Number)
        elif self.Type == GCodeCommandPartType.CharacterAndNumber:
            return self.Character + str(self.Number)
        elif self.Type == GCodeCommandPartType.Comment:
            return ';' + self.Text
        elif self.Type == GCodeCommandPartType.Text:
            return self.Text
        else:
            raise Exception("Internal error")

    def WriteTo(self, writer):
        if self.Type == GCodeCommandPartType.Space:
            writer.write(SpaceString.OfLength(self.Number))
        elif self.Type == GCodeCommandPartType.CharacterAndNumber:
            writer.write(self.Character)
            wholes = len(str(int(self.Number)))
            want_decimals = 5
            want_figures = want_decimals + wholes
            writer.write(
                ("{:."+str(want_figures)+"g}").format(self.Number)
            )
            # writer.write("%.5g" % self.Number)
            # ^ The format was "##0.#####" (# is optional) in C#
            #   (don't use g since though g makes decimals optional,
            #   .5g counts 5 INCLUDING before the decimal but we always
            #   want all 5 if present)
        elif self.Type == GCodeCommandPartType.Comment:
            writer.write(';')
            writer.write(self.Text)
        else:
            raise Exception("Internal error")

    @staticmethod
    def ParseStringToParts(line):
        results = []
        isFirstPart = True
        index = 0
        while index < len(line):
            if line[index] == ';':
                yield GCodeCommandPart(
                    Type=GCodeCommandPartType.Comment,
                    Text=line[index + 1:],
                )
                return
            if IsSpace(line[index]):
                count = 1
                index += 1
                while (index < len(line)) and IsSpace(line, index):
                    count += 1
                    index += 1
                yield GCodeCommandPart(
                    Type=GCodeCommandPartType.Space,
                    Number=count,
                )
            else:
                part = GCodeCommandPart(
                    Type=GCodeCommandPartType.CharacterAndNumber,
                    Character=line[index],
                )
                index += 1
                numberStart = index
                while ((index < len(line))
                       and not IsSpace(line, index)):
                    index += 1
                part.Number = ToNumber(line[numberStart:index])

                yield part
                wasFirstPart = isFirstPart
                isFirstPart = False
                if (wasFirstPart and (part.Character == 'M')
                        and ((part.Number == 117)
                             or (part.Number == 118))
                        and (index < len(line))):
                    # Return remainder of line as a single text block
                    count = 1
                    index += 1
                    while ((index < len(line))
                            and IsSpace(line, index)):
                        count += 1
                        index += 1

                    yield GCodeCommandPart(
                        Type=GCodeCommandPartType.Space,
                        Number=count,
                    )

                    if index < len(line):
                        yield GCodeCommandPart(
                            Type=GCodeCommandPartType.Text,
                            Text=line[index:],
                        )
                    return
