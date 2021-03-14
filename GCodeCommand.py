from System import *
# Processed by pycodetool https://github.com/poikilos/pycodetool2021-03-13 21:57:24
import sys
#from System.IO import *
#from System.Linq import *
#from System.Text import *

class GCodeCommand:
    def __init__(self, line):
        _parts = GCodeCommandPart.ParseStringToParts(line).ToArray()
        firstPart = _parts.FirstOrDefault()
        if firstPart is not None:
            self._CommandType = firstPart.Character
            self._CommandNumber = firstPart.Number
            self._Command = CommandCache.Get(self._CommandType, self._CommandNumber)

#    def ToString(self):
#        builder = StringBuilder()
#        enumerator = _parts.GetEnumerator()
#        while enumerator.MoveNext():
#            part = enumerator.Current
#            builder.Append(part)
#        return builder.ToString()
#
#    def WriteTo(self, writer):
#        enumerator = _parts.GetEnumerator()
#        while enumerator.MoveNext():
#            part = enumerator.Current
#            part.WriteTo(writer)
#
#    def HasParameter(self, v):
#        pass
