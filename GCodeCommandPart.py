from System import *
from System.Collections.Generic import *
from System.IO import *
from System.Text import *

class GCodeCommandPart(object):
    def __init__(self):

    def ToString(self):
        if self._Type == GCodeCommandPartType.Space:
            return SpaceString.OfLength(self._Number)
        elif self._Type == GCodeCommandPartType.CharacterAndNumber:
            return StringBuilder(capacity = 6).Append(self._Character).Append(self._Number).ToString()
        elif self._Type == GCodeCommandPartType.Comment:
            return ';' + self._Text
        elif self._Type == GCodeCommandPartType.Text:
            return self._Text
        else:
            raise Exception("Internal error")

    def WriteTo(self, writer):
        if self._Type == GCodeCommandPartType.Space:
            writer.Write(SpaceString.OfLength(self._Number))
        elif self._Type == GCodeCommandPartType.CharacterAndNumber:
            writer.Write(self._Character)
            writer.Write(self._Number.ToString("##0.#####"))
        elif self._Type == GCodeCommandPartType.Comment:
            writer.Write(';')
            writer.Write(self._Text)
        else:
            raise Exception("Internal error")

    def ParseStringToParts(line):
        isFirstPart = True
        index = 0
        while index < line.Length:
            if line[index] == ';':
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
                while (index < line.Length) and not Char.IsWhiteSpace(line, index):
                    index += 1
                part.Number = Decimal.Parse(line.Substring(numberStart, index - numberStart))
                wasFirstPart = isFirstPart
                isFirstPart = False
                if wasFirstPart and (part.Character == 'M') and ((part.Number == 117m) or (part.Number == 118m)) and (index < line.Length):
                    # Return remainder of line as a single text block
                    count = 1
                    index += 1
                    while (index < line.Length) and Char.IsWhiteSpace(line, index):
                        count += 1
                        index += 1
                    if index < line.Length:

    ParseStringToParts = staticmethod(ParseStringToParts)
