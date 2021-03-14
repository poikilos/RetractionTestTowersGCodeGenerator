#!/usr/bin/env python
# Processed by pycodetool https://github.com/poikilos/pycodetool
# 2021-03-14 10:52:20
# from System import *
# from System.Collections.Generic import *
# from System.IO import *
# from System.Linq import *
import sys
import os
from GCodeCommandPart import IsSpace

digits = "0123456789"

def IsNullOrWhiteSpace(s):
    if s is None:
        return True
    if len(s) == 0:
        return True
    return str.isspace(s)


class Extent:
    def __init__(self):
        self.From = 0.0
        self.To = 0.0

    @property
    def Middle(self):
        return self.From * 0.5 + self.To * 0.5

    def Extend(self, value):
        if not isinstance(value, float):
            raise ValueError("The value must be an float but"
                             " is \"{}\".".format(value))
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
        return CurvePoint.compare(self.Z, other.Z) < 0

    def __gt__(self, other):
        return CurvePoint.compare(self.Z, other.Z) > 0

    def __eq__(self, other):
        return CurvePoint.compare(self.Z, other.Z) == 0

    def __le__(self, other):
        return CurvePoint.compare(self.Z, other.Z) <= 0

    def __ge__(self, other):
        return CurvePoint.compare(self.Z, other.Z) >= 0

    def __ne__(self, other):
        return CurvePoint.compare(self.Z, other.Z) != 0


class GCodeWriter:
    def __init__(self, underlying):
        self._underlying = underlying
        self.NumLines = 0
        self.NumCommands = 0
        self.NumMovementCommands = 0
        self.NumCharactersWritten = 0

    def WriteLine(command):
        if isinstance(command, GCodeCommand):
            command = command.ToString()
        NumLines += 1
        if GCodeWriter.IsCommand(command):
            NumCommands += 1
            if GCodeWriter.IsMovementCommand(command):
                NumMovementCommands += 1
        NumCharactersWritten += len(command) + len(os.linesep)
        self._underlying.write(command + "\n")

    @staticmethod
    def IsCommand(line):
        i = -1
        while i + 1 < len(line):
            i += 1
            if IsSpace(line, i):
                continue
            if line[i] == ';':
                break
            if (line[i] == 'G') or (line[i] == 'M'):
                i += 1
                if i >= len(line):
                    return False
                return line[i] in digits
        return False

    @staticmethod
    def IsMovementCommand(command):
        for i in range(len(command)):
            if IsSpace(command, i):
                continue
            if command[i] == ';':
                break
            if command[i] == 'G':
                i += 1
                if i >= len(command):
                    return False
                if (command[i] != '0') and (command[i] != '1'):
                    return False
                i += 1
                return (i >= len(command)) or IsSpace(command[i])
        return False


class Program:

    FirstTowerZ = 2.1
    TEMPLATE_NAME = "Retraction Test Towers Template.gcode"
    DATA_DIR = os.path.dirname(os.path.abspath(__file__))

    @property
    def GraphRowHeight(self):
        return 0.5

    @staticmethod
    def GetTemplateReader():
        # formerly (nameof(RetractionTestTowersGCodeGenerator)
        # + ".Retraction Test Towers Template.gcode"))
        template_path = os.path.join(Program.DATA_DIR,
                                     Program.TEMPLATE_NAME)
        return open(template_path)

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

        # CHECK NEXT LINE for type declarations !!!
        while True:
            line = stream.readline()
            if not line:
                break
            line = line.rstrip()

            if IsNullOrWhiteSpace(line):
                continue

            command = GCodeCommand(line)

            if command.Command == "G1":
                if command.HasParameter('X'):
                    x.Extend(command.GetParameter('X'))
                if command.HasParameter('Y'):
                    y.Extend(command.GetParameter('Y'))

            if (command.Command == "G0") or (command.Command == "G1"):
                if command.HasParameter('Z'):
                    currentZ = command.GetParameter('Z')

                if command.HasParameter('E'):
                    e = command.GetParameter('E')

                    if (e > lastE) and (currentZ != sys.float_info.min):
                        lastE = e
                        z.Extend(currentZ)

        return (x, y, z)

    @classmethod
    def Main(cls, args):
        extents = Program.MeasureGCode(Program.GetTemplateReader())

        print("Template extents:")

        print("    From     Centre   To")
        print("X   {0,5:##0.0}    {1,5:##0.0}    {2,5:##0.0}", extents.X.From, extents.X.Middle, extents.X.To)
        print("Y   {0,5:##0.0}    {1,5:##0.0}    {2,5:##0.0}", extents.Y.From, extents.Y.Middle, extents.Y.To)
        print("Z   {0,5:##0.0}    {1,5:##0.0}    {2,5:##0.0}", extents.Z.From, extents.Z.Middle, extents.Z.To)

        curvePoints = []

        deltaX = 0.0
        deltaY = 0.0

        outputFileName = "RetractionTest.gcode"

        if len(args) == 0:
            curvePoints.append(
                CurvePoint(
                    PointType = CurvePointType.SameValueUntil,
                    Z = FirstTowerZ,
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
        else:
            index = 0

            # CHECK NEXT LINE for type declarations !!!
            while index < len(args):
                curvePoint = CurvePoint()

                argName = args[index].lower()

                if argName == "/output":
                    outputFileName = args[index + 1]
                    index += 1

                    continue
                elif argName == "/center":
                    deltaX = float(args[index + 1]) - extents.X.Middle
                    deltaY = float(args[index + 2]) - extents.Y.Middle

                    index += 3

                    continue
                elif argName == "/startwith":
                    initialPoint = CurvePoint()

                    initialPoint.PointType = CurvePointType.SameValueUntil
                    initialPoint.Z = FirstTowerZ
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

        print("")

        if (deltaX != 0) or (deltaY != 0):
            print(
                "Will translate test print to be centred at ({0:##0.0}"
                ", {1:##0.0})".format(
                    extents.X.Middle + deltaX,
                    extents.Y.Middle + deltaY,
                )
            )
            print("")

        print("Z    ? Retraction")

        lastCurvePointsPassed = 0

        z = 17.0
        while z >= FirstTowerZ - self.GraphRowHeight:
            lastExtraRow = False
            if z < FirstTowerZ:
                lastExtraRow = True
                z = FirstTowerZ
            sys.stdout.write(z.ToString("#0.0").rjust(4))
            sys.stdout.write(' ')
            curvePointsPassed = \
                sum(1 for point in curvePoints if point.Z >= z)
            if curvePointsPassed == lastCurvePointsPassed:
                sys.stdout.write("  ")
            else:
                sys.stdout.write("+ ")
                lastCurvePointsPassed = curvePointsPassed
            retraction = Program.GetRetractionForZ(z, curvePoints)
            sys.stdout.write(retraction.ToString("#0.0000 ").rjust(8))
            barWidth = int(round(retraction * 5))
            for i in range(barWidth):
                sys.stdout.write('*')
            print("")
            if lastExtraRow:
                break
            z -= self.GraphRowHeight

        print("")
        print("Will write output to: {0}".format(outputFileName))

        with open(outputFileName, 'w') as writer:
            print("")
            print("Generating G code...")

            Program.TranslateGCode(
                Program.GetTemplateReader(),
                writer,
                FirstTowerZ,
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

            # CHECK NEXT LINE for type declarations !!!
            while True:
                line = stream.readline()
                if not line:
                    break
                line = line.rstrip()

                command = GCodeCommand(line)

                if (command.Command == "G0") or (command.Command == "G1"):
                    if command.HasParameter('Z'):
                        z = command.GetParameter('Z')

                    if command.HasParameter('E'):
                        e = command.GetParameter('E')

                        if e < lastE:
                            print("=> Retract by {lastE - e} at Z {z}"
                                  "".format(lastE=lastE,e=e,z=z))
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

        # CHECK NEXT LINE for type declarations !!!
        while True:
            line = stream.readline()
            if not line:
                break
            line = line.rstrip()

            command = GCodeCommand(line)

            if (command.Command == "G0") or (command.Command == "G1"):
                if command.HasParameter('X'):
                    command.SetParameter('X', command.GetParameter('X') + deltaX)
                if command.HasParameter('Y'):
                    command.SetParameter('Y', command.GetParameter('Y') + deltaY)

                if command.HasParameter('Z'):
                    z = command.GetParameter('Z')

                    if uniqueZValues.append(z):
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
                                "dE {retraction:0.000} at Z {z:#0.0}"
                            ).format(retraction=retraction, z=z)
                            serialMessage = (
                                "Retraction {retraction:0.00000}"
                                " at Z {z:#0.0}"
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
        print("- {0} unique Z values".format(uniqueZValues.Count))
        print("- {0} retractions".format(numberOfRetractions))

    @staticmethod
    def GetRetractionForZ(z, curvePoints):
        if not isinstance(z, float):
            raise ValueError("The z must be an float but"
                             " is \"{}\".".format(z))
        if not isinstance(curvePoints, list):
            raise ValueError("The curvePoints must be a list but"
                             " is \"{}\".".format(curvePoints))
        previousPoint = curvePoints[0]

        # CHECK NEXT LINE for type declarations !!!
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
