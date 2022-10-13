#!/usr/bin/env python
# Processed by pycodetool https://github.com/poikilos/pycodetool
# 2021-03-13 21:54:12
# from System import *
# from System.Collections.Generic import *
# from System.IO import *
# from System.Text import *
import sys

from retractiontower.gcodecommandparttype import GCodeCommandPartType
from retractiontower.spacestring import SpaceString
from retractiontower.fxshim import (
    IsWhiteSpace,
    decimal_Parse,
    NumberToStr,
    IsNullOrWhiteSpace,
    optionalD,
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
    COMMENT_MARKS = [';', '//']
    F_PARAMS = "XY"  # ZE"  # always convert to float

    def __init__(self, **kwargs):
        self.Type = kwargs.get("Type")
        self.Character = kwargs.get("Character")
        self.Number = kwargs.get("Number")
        self.Text = kwargs.get("Text")
        self.CommentMark = kwargs.get("CommentMark")

    def __str__(self):
        return self.ToString()

    def __repr__(self):
        # This is used when a list containing this is formatted as text.
        return self.ToString()

    def ToString(self):
        if self.Type == GCodeCommandPartType.Space:
            return SpaceString.OfLength(self.Number)
        elif self.Type == GCodeCommandPartType.CharacterAndNumber:
            if self.Character in GCodeCommandPart.F_PARAMS:
                return self.Character + optionalD(float(self.Number), 3).format(float(self.Number))
            return self.Character + NumberToStr(self.Number)
        elif self.Type == GCodeCommandPartType.Character:
            return self.Character
        elif self.Type == GCodeCommandPartType.Comment:
            commentMark = self.CommentMark
            if IsNullOrWhiteSpace(self.CommentMark):
                commentMark = ';'
            return commentMark + self.Text
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
            # writer.write(
            #     ("{:."+str(want_figures)+"g}").format(self.Number)
            # )
            writer.write(optionalD(self.Number, want_decimals).format(self.Number))
            # writer.write("%.5g" % self.Number)
            # ^ The format was "##0.#####" (# is optional) in C#
            #   (don't use g since though g makes decimals optional,
            #   .5g counts 5 INCLUDING before the decimal but we always
            #   want all 5 if present)
        elif self.Type == GCodeCommandPartType.Comment:
            if not IsNullOrWhiteSpace(self.CommentMark):
                writer.write(self.CommentMark)
            else:
                writer.write(';')
            writer.write(self.Text)
        else:
            raise Exception("Internal error")

    @staticmethod
    def commentMarkAt(line, i):
        '''
        Get the comment mark at i in line, or return None if there is
        not a comment mark there.
        '''
        for cm in GCodeCommandPart.COMMENT_MARKS:
            if line[i:i+len(cm)] == cm:
                return cm
        return None

    def isCommentAt(line, i):
        '''
        Return True if there is a comment mark at i in line.
        Otherwise, return False.
        '''
        return GCodeCommandPart.commentMarkAt(line, i) is not None

    @staticmethod
    def ParseStringToParts(line, path=None, line_n=None):
        results = []
        isFirstPart = True
        index = 0

        while index < len(line):
            commentMark = GCodeCommandPart.commentMarkAt(line, index)
            if commentMark is not None:
                yield GCodeCommandPart(
                    Type=GCodeCommandPartType.Comment,
                    Text=line[index + len(commentMark):],
                    CommentMark=commentMark,
                )
                return
            if IsWhiteSpace(line[index]):
                count = 1
                index += 1
                while (index < len(line)) and IsWhiteSpace(line, index):
                    count += 1
                    index += 1
                yield GCodeCommandPart(
                    Type=GCodeCommandPartType.Space,
                    Number=count,
                )
            else:
                start = index
                part = GCodeCommandPart(
                    Type=GCodeCommandPartType.CharacterAndNumber,
                    Character=line[index],
                )
                index += 1
                numberStart = index
                while ((index < len(line))
                       and not IsWhiteSpace(line, index)
                       and not GCodeCommandPart.isCommentAt(line, index)):
                    index += 1
                numberStr = line[numberStart:index]
                if len(numberStr) == 0:
                    part = GCodeCommandPart(
                        Type=GCodeCommandPartType.Character,
                        Character=line[start],
                    )
                else:
                    try:
                        part.Number = decimal_Parse(numberStr)
                    except ValueError as ex:
                        print(
                            "{}:{}: Error parsing line: `{}` substring `{}`"
                            "".format(path, line_n, line, line[numberStart:index])
                        )
                        raise

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
                            and IsWhiteSpace(line, index)):
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
