#!/usr/bin/env python
'''
Retraction Tower Processor
--------------------------
This program processes template gcode to produce RetractionTower.gcode.
https://github.com/poikilos/RetractionTowerProcessor is a
Python reinterpretation of logiclrd's C# RetractionTestTowersGCodeGenerator.

Options:
/output  <path>            Specify where to save the gcode
                           (default: RetractionTower.gcode).
/center <x> <y>            Set the middle for calculating extents.
/template <path>           Choose an input gcode file.
/startwith <retraction>    Start with this retraction length (default 2).
/setat <z>                 Keep the same retraction up to here (default 2).
/interpolateto <z> <retr.> Interpolate up to here and to this retraction
                           (default z=32,
                           default retraction startwith + .5 per mm).
/checkfile                 Check the file only.
'''
# Processed by pycodetool https://github.com/poikilos/pycodetool
# 2021-03-14 10:52:20
# from System import *
# from System.Collections.Generic import *
# from System.IO import *
# from System.Linq import *
import sys
import os
from retractiontower.fxshim import (
    IsWhiteSpace,
    decimal_Parse,
    IsNullOrWhiteSpace,
    IsDigit,
)
from retractiontower.gcodecommand import GCodeCommand
from retractiontower.gcodecommandpart import GCodeCommandPart


def usage():
    print(__doc__)


def peek_line(f):
    # as per <https://stackoverflow.com/a/16840747/4541104>
    pos = f.tell()
    line = f.readline()
    f.seek(pos)
    return line


class Extent:
    def __init__(self):
        self.From = 0.0
        self.To = 0.0

    @property
    def Middle(self):
        return self.From * 0.5 + self.To * 0.5

    def Extend(self, value, tbs=None):
        '''
        Keyword arguments:
        tbs -- a string to display on error (put the line of G-code or
               something else useful in here as some form of traceback
               string).
        '''
        if isinstance(value, int):
            msg = "."
            if tbs is not None:
                msg = " while \"{}\".".format(tbs)
            print("Warning: The value should be an float but"
                  " is \"{}\"".format(value) + msg)
            value = float(value)
        if not isinstance(value, float):
            msg = "."
            if tbs is not None:
                msg = " while \"{}\".".format(tbs)
            raise ValueError("The value must be an float but"
                             " is \"{}\"".format(value) + msg)
        if value < self.From:
            self.From = value
        if value > self.To:
            self.To = value


# enum CurvePointType
class CurvePointType:
    SameValueUntil = 0
    InterpolateUpTo = 1


class CurvePoint:
    '''
    members:
    PointType -- a value that matches a constant in CurvePointType
    '''
    def __init__(self, **kwargs):
        self.PointType = kwargs.get('PointType')
        self.Z = kwargs.get('Z')
        self.Retraction = kwargs.get('Retraction')

    @staticmethod
    def compare(curvepoint1, curvepoint2):
        return curvepoint1.Z - curvepoint2.Z

    def __lt__(self, other):
        return CurvePoint.compare(self, other) < 0

    def __gt__(self, other):
        return CurvePoint.compare(self, other) > 0

    def __eq__(self, other):
        return CurvePoint.compare(self, other) == 0

    def __le__(self, other):
        return CurvePoint.compare(self, other) <= 0

    def __ge__(self, other):
        return CurvePoint.compare(self, other) >= 0

    def __ne__(self, other):
        return CurvePoint.compare(self, other) != 0


class GCodeWriter:
    def __init__(self, underlying):
        self._underlying = underlying
        self.NumLines = 0
        self.NumCommands = 0
        self.NumMovementCommands = 0
        self.NumCharactersWritten = 0

    def WriteLine(self, command):
        if isinstance(command, GCodeCommand):
            command = command.ToString()
        self.NumLines += 1
        if GCodeWriter.IsCommand(command):
            self.NumCommands += 1
            if GCodeWriter.IsMovementCommand(command):
                self.NumMovementCommands += 1
        self.NumCharactersWritten += len(command) + len(os.linesep)
        self._underlying.write(command + "\n")

    @staticmethod
    def IsCommand(line):
        i = -1
        while i + 1 < len(line):
            i += 1
            if IsWhiteSpace(line, i):
                continue
            if GCodeCommandPart.isCommentAt(line, i):
                break
            if (line[i] == 'G') or (line[i] == 'M'):
                i += 1
                if i >= len(line):
                    return False
                return IsDigit(line[i])
        return False

    @staticmethod
    def IsMovementCommand(command):
        i = -1
        while i + 1 < len(command):
            i += 1
            if IsWhiteSpace(command, i):
                continue
            if GCodeCommandPart.isCommentAt(command, i):
                break
            if command[i] == 'G':
                i += 1
                if i >= len(command):
                    return False
                if (command[i] != '0') and (command[i] != '1'):
                    return False
                i += 1
                return (i >= len(command)) or IsWhiteSpace(command[i])
        return False


class Program:
    _FirstTowerZ = 2.1
    _GraphRowHeight = 0.5
    _DEFAULT_TEMPLATE_NAME = "Template.gcode"
    DATA_DIR = os.path.dirname(os.path.abspath(__file__))
    MODEL_PATH = os.path.join(DATA_DIR, "Model",
                              "RetractionTestCylinders.stl")
    # TEMPLATE_PATH = os.path.join(DATA_DIR, _DEFAULT_TEMPLATE_NAME)
    TEMPLATE_PATH = os.path.join(os.getcwd(), _DEFAULT_TEMPLATE_NAME)
    _extents = None
    _extents_done = False

    @staticmethod
    def get_FirstTowerZ():
        return Program._FirstTowerZ

    @staticmethod
    def get_GraphRowHeight():
        return Program._GraphRowHeight

    @staticmethod
    def getTemplateUsage():
        msg = (
             "You must specify a template path or\n"
             " generate the G-code file \"{}\""
             " from \"{}\" using your slicer software."
             "".format(Program.TEMPLATE_PATH,
                       Program.MODEL_PATH)
        )
        return msg

    @staticmethod
    def GetTemplateReader():
        # formerly (nameof(RetractionTestTowersGCodeGenerator)
        # + ".Retraction Test Towers Template.gcode"))
        if not os.path.isfile(Program.TEMPLATE_PATH):
            raise ValueError(Program.getTemplateUsage())
            # return None
        return open(Program.TEMPLATE_PATH)

    @staticmethod
    def MeasureGCode(stream):
        #  Count only G1 moves in X and Y.
        #  Count G0 and G1 moves in Z, but only for Z values
        #    where filament is extruded.
        x = Extent()
        y = Extent()
        z = Extent()

        x.From = y.From = z.From = sys.float_info.max
        x.To = y.To = z.To = sys.float_info.min
        lastE = sys.float_info.min
        currentZ = sys.float_info.min
        zTBS = None

        while True:
            line = stream.readline()
            if not line:
                break
            line = line.rstrip("\n\r")

            if IsNullOrWhiteSpace(line):
                continue

            command = GCodeCommand(line)

            if command.Command == "G1":
                if command.HasParameter('X'):
                    x.Extend(
                        command.GetParameter('X'),
                        tbs="on X where line=\"{}\"".format(line)
                    )
                if command.HasParameter('Y'):
                    y.Extend(
                        command.GetParameter('Y'),
                        tbs="on Y where line=\"{}\"".format(line)
                    )

            if (command.Command == "G0") or (command.Command == "G1"):
                if command.HasParameter('Z'):
                    currentZ = command.GetParameter('Z')
                    zTBS = ("z originated from line=\"{}\""
                            "".format(line))

                if command.HasParameter('E'):
                    e = command.GetParameter('E')

                    if (e > lastE) and (currentZ != sys.float_info.min):
                        lastE = e
                        z.Extend(
                            currentZ,
                            tbs=("on Z where line=\"{}\" and {}"
                                 "").format(line, zTBS)
                        )

        class AnonymousClass:
            pass
        result = AnonymousClass()
        result.X = x
        result.Y = y
        result.Z = z
        return result

    @classmethod
    def CalculateExtents(cls):
        if not os.path.isfile(cls.TEMPLATE_PATH):
            return False
        cls._extents_done = False
        reader = cls.GetTemplateReader()
        try:
            cls._extents = cls.MeasureGCode(reader)
            cls._extents_done = True
        finally:
            reader.close()

        if cls._extents_done:
            print("Template extents:")

            print("    From     Centre   To")
            print("X   {0: >5.1f}    {1: >5.1f}    {2: >5.1f}"
                  "".format(cls._extents.X.From, cls._extents.X.Middle,
                            cls._extents.X.To))
            print("Y   {0: >5.1f}    {1: >5.1f}    {2: >5.1f}"
                  "".format(cls._extents.Y.From, cls._extents.Y.Middle,
                            cls._extents.Y.To))
            print("Z   {0: >5.1f}    {1: >5.1f}    {2: >5.1f}"
                  "".format(cls._extents.Z.From, cls._extents.Z.Middle,
                            cls._extents.Z.To))
        return cls._extents_done

    @classmethod
    def Main(cls, args):
        cls.CalculateExtents()

        curvePoints = []

        deltaX = 0.0
        deltaY = 0.0

        outputFileName = "RetractionTest.gcode"
        extents_used_by = None
        center = None

        if True:
            index = 0

            while index < len(args):
                curvePoint = CurvePoint()

                argName = args[index].lower()

                if argName == "/output":
                    outputFileName = args[index + 1]
                    index += 2
                    continue

                elif argName == "/center":
                    if not cls._extents_done:
                        raise ValueError(Program.getTemplateUsage())
                    center = (float(args[index + 1]),
                              float(args[index + 2]))
                    deltaX = center[0] - cls._extents.X.Middle
                    deltaY = center[1] - cls._extents.Y.Middle
                    index += 3
                    extents_used_by = "/center"
                    continue

                elif argName == "/template":
                    cls.TEMPLATE_PATH = args[index + 1]
                    cls.CalculateExtents()
                    if extents_used_by == "/center":
                        deltaX = center[0] - cls._extents.X.Middle
                        deltaY = center[1] - cls._extents.Y.Middle
                    elif extents_used_by is not None:
                        raise NotImplementedError(
                            "The program cannot recalculate the"
                            " effect of {} after changing the model."
                        )
                    index += 2
                    continue

                elif argName == "/startwith":
                    initialPoint = CurvePoint()
                    initialPoint.PointType = CurvePointType.SameValueUntil
                    initialPoint.Z = cls.get_FirstTowerZ()
                    initialPoint.Retraction = float(args[index + 1])
                    curvePoints.append(initialPoint)
                    index += 2
                    continue

                elif ((argName == "/setat")
                        or (argName == "/interpolateto")):
                    if argName == "/setat":
                        curvePoint.PointType = CurvePointType.SameValueUntil
                    else:
                        curvePoint.PointType = CurvePointType.InterpolateUpTo

                    curvePoint.Z = float(args[index + 1])
                    curvePoint.Retraction = float(args[index + 2])
                    curvePoints.append(curvePoint)
                    index += 3
                    continue

                elif argName == "/checkfile":
                    cls.AnalyzeFile(args[index + 1])
                    return 0
                elif argName in ["--help", "/?"]:
                    usage()
                    return 0

                raise Exception("Invalid command-line format")
        if (not os.path.isfile(cls.TEMPLATE_PATH)
                or (not cls._extents_done)):
            raise ValueError(Program.getTemplateUsage())
        if len(curvePoints) == 0:
            curvePoints.append(
                CurvePoint(
                    PointType=CurvePointType.SameValueUntil,
                    Z=cls.get_FirstTowerZ(),
                    Retraction=2.0,
                )
            )

            curvePoints.append(
                CurvePoint(
                    PointType=CurvePointType.InterpolateUpTo,
                    Z=cls._extents.Z.To,
                    Retraction=3.0,
                )
            )

        print("")

        if (deltaX != 0) or (deltaY != 0):
            print(
                "Will translate test print to be centered at ({0:.1f}"
                ", {1:.1f})".format(
                    cls._extents.X.Middle + deltaX,
                    cls._extents.Y.Middle + deltaY,
                )
            )
            print("")

        print("Z    ? Retraction")

        lastCurvePointsPassed = 0

        # z = 17.0  # for original
        z = 32.0
        span = cls.get_FirstTowerZ() - cls.get_GraphRowHeight()
        while z >= span:
            lastExtraRow = False
            if z < cls.get_FirstTowerZ():
                lastExtraRow = True
                z = cls.get_FirstTowerZ()
            sys.stdout.write("{:.1f}".format(z).rjust(4))
            sys.stdout.write(' ')
            curvePointsPassed = \
                sum(1 for point in curvePoints if point.Z >= z)
            if curvePointsPassed == lastCurvePointsPassed:
                sys.stdout.write("  ")
            else:
                sys.stdout.write("+ ")
                lastCurvePointsPassed = curvePointsPassed
            retraction = cls.GetRetractionForZ(z, curvePoints)
            sys.stdout.write("{:.4f} ".format(retraction).rjust(8))
            barWidth = int(round(retraction * 5))
            for i in range(barWidth):
                sys.stdout.write('*')
            print("")
            if lastExtraRow:
                break
            z -= cls.get_GraphRowHeight()

        print("")
        print("Will write output to: {0}".format(outputFileName))

        with open(outputFileName, 'w') as writer:
            print("")
            print("Generating G code...")

            cls.TranslateGCode(
                cls.GetTemplateReader(),
                writer,
                cls.get_FirstTowerZ(),
                deltaX,
                deltaY,
                curvePoints,
            )

        print("")
        print(os.path.abspath(outputFileName))
        return 0

    @staticmethod
    def AnalyzeFile(fileName):
        with open(fileName, 'r') as reader:
            z = sys.float_info.min
            lastE = sys.float_info.min

            while True:
                line = reader.readline()
                if not line:
                    break
                line = line.rstrip("\n\r")

                command = GCodeCommand(line)

                if (command.Command == "G0") or (command.Command == "G1"):
                    if command.HasParameter('Z'):
                        z = command.GetParameter('Z')

                    if command.HasParameter('E'):
                        e = command.GetParameter('E')

                        if e < lastE:
                            print("=> Retract by {0} at Z {z}"
                                  "".format(lastE-e, z=z))
                        else:
                            lastE = e
        return 0

    @staticmethod
    def TranslateGCode(reader, writer, firstTowerZ, deltaX, deltaY,
                       curvePoints):
        if not isinstance(firstTowerZ, float):
            raise ValueError("The firstTowerZ must be an float but"
                             " is \"{}\".".format(firstTowerZ))
        if not isinstance(curvePoints, list):
            raise ValueError("The curvePoints must be a list but"
                             " is \"{}\".".format(curvePoints))

        curvePoints = sorted(curvePoints)
        z = sys.float_info.min
        uniqueZValues = set()
        lastE = sys.float_info.min
        lastSerialMessage = ""
        gcodeWriter = GCodeWriter(writer)
        numberOfRetractions = 0

        line_n = 0
        is_relative = False
        while True:
            line_n += 1
            line = reader.readline()
            if not line:
                break
            line = line.rstrip("\n\r")

            command = GCodeCommand(line)

            if (command.Command == "G0") or (command.Command == "G1"):
                if command.HasParameter('X'):
                    command.SetParameter(
                        'X',
                        command.GetParameter('X') + deltaX
                    )
                if command.HasParameter('Y'):
                    command.SetParameter(
                        'Y',
                        command.GetParameter('Y') + deltaY
                    )

                if command.HasParameter('Z'):
                    z = command.GetParameter('Z')

                    if uniqueZValues.add(z):
                        sys.stdout.write('#')

                if z >= firstTowerZ:
                    if command.HasParameter('E'):
                        e = command.GetParameter('E')

                        if e < lastE:
                            #  Retraction!
                            numberOfRetractions += 1

                            retraction = Program.GetRetractionForZ(
                                z,
                                curvePoints
                            )
                            if is_relative:
                                # Don't change relative extrusion
                                #   such as end G-code.
                                newE = retraction
                                if e < 0:
                                    newE *= -1.0
                            else:
                                newE = lastE - retraction
                            command.SetParameter('E', newE)

                            lcdScreenMessage = (
                                "dE {retraction:.3f} at Z {z:.1f}"
                            ).format(retraction=retraction, z=z)
                            serialMessage = (
                                "Retraction {retraction:.5f}"
                                " at Z {z:.1f}"
                            ).format(retraction=retraction, z=z)

                            gcodeWriter.WriteLine("M117 " + lcdScreenMessage)

                            if serialMessage != lastSerialMessage:
                                gcodeWriter.WriteLine("M118 " + serialMessage)

                                lastSerialMessage = serialMessage

                        lastE = e
            elif command.Command == "G91":
                is_relative = True
            elif command.Command == "G90":
                is_relative = False

            gcodeWriter.WriteLine(command)

        print("")
        print("")
        print("Output:")
        print("- {0} characters".format(gcodeWriter.NumCharactersWritten))
        print("- {0} lines".format(gcodeWriter.NumLines))
        print("- {0} commands".format(gcodeWriter.NumCommands))
        print("- {0} movement commands".format(gcodeWriter.NumMovementCommands))
        print("- {0} unique Z values".format(len(uniqueZValues)))
        print("- {0} retractions".format(numberOfRetractions))

    @staticmethod
    def GetRetractionForZ(z, curvePoints):
        if isinstance(z, int):
            msg = "."
            if tbs is not None:
                msg = " while \"{}\".".format(tbs)
            print("Warning: The z should be an float but"
                  " is \"{}\"".format(z) + msg)
            z = float(z)
        if not isinstance(z, float):
            raise ValueError("The z must be an float but"
                             " is \"{}\".".format(z))
        if not isinstance(curvePoints, list):
            raise ValueError("The curvePoints must be a list but"
                             " is \"{}\".".format(curvePoints))
        previousPoint = curvePoints[0]

        for point in curvePoints:
            if point.Z >= z:
                if point.PointType == CurvePointType.SameValueUntil:
                    return previousPoint.Retraction

                interpolateFrom = previousPoint.Retraction
                interpolateTo = point.Retraction

                interpolateFromZ = previousPoint.Z
                interpolateToZ = point.Z

                interpolateRange = interpolateToZ - interpolateFromZ

                weightTo = (z - previousPoint.Z) / interpolateRange
                weightFrom = (point.Z - z) / interpolateRange

                result = interpolateFrom * weightFrom + interpolateTo * weightTo
                if result > interpolateTo:
                    print(
                        'Warning: result {} > interpolateTo {}'
                        ' (interpolateRange={}, interpolateToZ={}, z={},'
                        ' weightFrom={}, weightTo={})'
                        ''.format(result, interpolateTo, interpolateRange,
                                  interpolateToZ, z, weightFrom, weightTo)
                    )

                return result

            previousPoint = point
        return curvePoints[-1].Retraction


def main():
    return Program.Main(sys.argv[1:])


if __name__ == "__main__":
    sys.exit(main())
