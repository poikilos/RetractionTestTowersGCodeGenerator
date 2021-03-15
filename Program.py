#!/usr/bin/env python
# Processed by pycodetool https://github.com/poikilos/pycodetool
# 2021-03-14 10:52:20
# from System import *
# from System.Collections.Generic import *
# from System.IO import *
# from System.Linq import *
import sys
import os
from cc0code import (
    IsWhiteSpace,
    decimal_Parse,
    IsNullOrWhiteSpace,
    IsDigit,
)
from GCodeCommand import GCodeCommand

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
            self.From = value;
        if value > self.To:
            self.To = value;


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
    def compare(l, r):
        return l.Z - r.Z

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
            if (line[i] == ';') or (line[i:i+2] == '//'):
                break
            if (line[i] == 'G') or (line[i] == 'M'):
                i += 1
                if i >= len(line):
                    return False
                return IsDigit(line[i])
        return False

    @staticmethod
    def IsMovementCommand(command):
        for i in range(len(command)):
            if IsWhiteSpace(command, i):
                continue
            if (command[i] == ';') or (command[i:i+2] == '//'):
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
    _DEFAULT_TEMPLATE_NAME = "RetractionTestTemplate.gcode"
    DATA_DIR = os.path.dirname(os.path.abspath(__file__))
    MODEL_PATH = os.path.join(DATA_DIR, "Model",
                              "RetractionTestCylinders.stl")
    TEMPLATE_PATH = os.path.join(DATA_DIR, _DEFAULT_TEMPLATE_NAME)

    @staticmethod
    def get_FirstTowerZ():
        return Program._FirstTowerZ

    @staticmethod
    def get_GraphRowHeight():
        return Program._GraphRowHeight

    @staticmethod
    def GetTemplateReader():
        # formerly (nameof(RetractionTestTowersGCodeGenerator)
        # + ".Retraction Test Towers Template.gcode"))
        if not os.path.isfile(Program.TEMPLATE_PATH):
            raise ValueError("You must specify a template path or\n"
                             " generate the G-code file \"{}\""
                             " from \"{}\" using your slicer software."
                             "".format(Program.TEMPLATE_PATH,
                                       Program.MODEL_PATH))
            return None
        return open(Program.TEMPLATE_PATH)

    @staticmethod
    def MeasureGCode(stream):
        #  Count only G1 moves in X and Y.
        #  Count G0 and G1 moves in Z, but only for Z values where filament is extruded.
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
    def Main(cls, args):
        reader = Program.GetTemplateReader()
        try:
            extents = Program.MeasureGCode(reader)
        finally:
            reader.close()

        print("Template extents:")

        print("    From     Centre   To")
        print("X   {0: >5.1f}    {1: >5.1f}    {2: >5.1f}"
              "".format(extents.X.From, extents.X.Middle, extents.X.To))
        print("Y   {0: >5.1f}    {1: >5.1f}    {2: >5.1f}"
              "".format(extents.Y.From, extents.Y.Middle, extents.Y.To))
        print("Z   {0: >5.1f}    {1: >5.1f}    {2: >5.1f}"
              "".format(extents.Z.From, extents.Z.Middle, extents.Z.To))


        curvePoints = []

        deltaX = 0.0
        deltaY = 0.0

        outputFileName = "RetractionTest.gcode"

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
                    deltaX = float(args[index + 1]) - extents.X.Middle
                    deltaY = float(args[index + 2]) - extents.Y.Middle
                    index += 3
                    continue

                elif argName == "/template":
                    Program.TEMPLATE_PATH = args[index + 1]
                    index += 2
                    continue

                elif argName == "/startwith":
                    initialPoint = CurvePoint()
                    initialPoint.PointType = CurvePointType.SameValueUntil
                    initialPoint.Z = Program.get_FirstTowerZ()
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
                    Program.AnalyzeFile(args[index + 1])
                    return

                raise Exception("Invalid command-line format")
        if len(curvePoints) == 0:
            curvePoints.append(
                CurvePoint(
                    PointType = CurvePointType.SameValueUntil,
                    Z = Program.get_FirstTowerZ(),
                    Retraction = 2.0,
                )
            )

            curvePoints.append(
                CurvePoint(
                    PointType = CurvePointType.InterpolateUpTo,
                    Z = extents.Z.To,
                    Retraction = 3.0,
                )
            )

        print("")

        if (deltaX != 0) or (deltaY != 0):
            print(
                "Will translate test print to be centered at ({0:.1f}"
                ", {1:.1f})".format(
                    extents.X.Middle + deltaX,
                    extents.Y.Middle + deltaY,
                )
            )
            print("")

        print("Z    ? Retraction")

        lastCurvePointsPassed = 0

        z = 17.0
        span = Program.get_FirstTowerZ() - Program.get_GraphRowHeight()
        while z >= span:
            lastExtraRow = False
            if z < Program.get_FirstTowerZ():
                lastExtraRow = True
                z = Program.get_FirstTowerZ()
            sys.stdout.write("{:.1f}".format(z).rjust(4))
            sys.stdout.write(' ')
            curvePointsPassed = \
                sum(1 for point in curvePoints if point.Z >= z)
            if curvePointsPassed == lastCurvePointsPassed:
                sys.stdout.write("  ")
            else:
                sys.stdout.write("+ ")
                lastCurvePointsPassed = curvePointsPassed
            retraction = Program.GetRetractionForZ(z, curvePoints)
            sys.stdout.write("{:.4f} ".format(retraction).rjust(8))
            barWidth = int(round(retraction * 5))
            for i in range(barWidth):
                sys.stdout.write('*')
            print("")
            if lastExtraRow:
                break
            z -= Program.get_GraphRowHeight()

        print("")
        print("Will write output to: {0}".format(outputFileName))

        with open(outputFileName, 'w') as writer:
            print("")
            print("Generating G code...")

            Program.TranslateGCode(
                Program.GetTemplateReader(),
                writer,
                Program.get_FirstTowerZ(),
                deltaX,
                deltaY,
                curvePoints,
            )

        print("")
        print(os.path.abspath(outputFileName))

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

    @staticmethod
    def TranslateGCode(reader, writer, firstTowerZ, deltaX, deltaY, curvePoints):
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
        while True:
            line_n += 1
            line = reader.readline()
            if not line:
                break
            line = line.rstrip("\n\r")

            command = GCodeCommand(line)

            if (command.Command == "G0") or (command.Command == "G1"):
                if command.HasParameter('X'):
                    command.SetParameter('X', command.GetParameter('X') + deltaX)
                if command.HasParameter('Y'):
                    command.SetParameter('Y', command.GetParameter('Y') + deltaY)

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

                            retraction = Program.GetRetractionForZ(z, curvePoints)

                            command.SetParameter('E', lastE - retraction)

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

            gcodeWriter.WriteLine(command)

        gcodeWriter.WriteLine("G0 X0 Y0")

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

                return interpolateFrom * weightFrom + interpolateTo * weightTo

            previousPoint = point

        return curvePoints[-1].Retraction


if __name__ == "__main__":
    Program.Main(sys.argv[1:])
