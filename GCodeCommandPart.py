#!/usr/bin/env python
# Processed by pycodetool https://github.com/poikilos/pycodetool
# 2021-03-13 21:54:12
# from System import *
# from System.Collections.Generic import *
# from System.IO import *
# from System.Text import *

from GCodeCommandPartType import GCodeCommandPartType

import sys


def IsSpace(*args):
    '''
    Sequential arguments:
    1st (args[0]) -- String to check as a whole or as a character
    2nd (args[1]) -- If present, the second param is the index in
                     args[0] to check and no other parts of args[0] will
                     be checked.
    '''
    if len(args) == 1:
        return str.isspace(args[0])
    elif len(args) == 2:
        return str.isspace(args[0][args[1]])
    raise ValueError("IsSpace only takes (charStr)"
                     " or (str, index)")


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
        self.Type = None
        self.Character = None
        self.Number = None
        self.Text = None

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
            writer.write("%.3g" % self.Number)
            # ^ The format was "##0.#####" (# is optional) in C#
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
                tmp = GCodeCommandPart()
                tmp.Type = GCodeCommandPartType.Comment
                tmp.Text = line[index + 1:]
                yield tmp
                raise StopIteration
            if IsSpace(line[index]):
                count = 1
                index += 1
                while (index < len(line)) and IsSpace(line, index):
                    count += 1
                    index += 1
                tmp = GCodeCommandPart()
                tmp.Type = GCodeCommandPartType.Space
                tmp.Number = count
                yield tmp
            else:
                part = GCodeCommandPart()
                part.Type = GCodeCommandPartType.CharacterAndNumber
                part.Character = line[index]
                index += 1
                numberStart = index
                while ((index < len(line))
                       and not IsSpace(line, index)):
                    index += 1
                part.Number = float(line[numberStart:index])
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

                    tmp = GCodeCommandPart()
                    tmp.Type = GCodeCommandPartType.Space
                    tmp.Number = count
                    yield tmp

                    if index < len(line):
                        tmp = GCodeCommandPart()
                        tmp.Type = GCodeCommandPartType.Text
                        tmp.Text = line[index:]
                        yield tmp
                    raise StopIteration
        # TODO: raise StopIteration?
