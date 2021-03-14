#!/usr/bin/env python
# Processed by pycodetool https://github.com/poikilos/pycodetool
# 2021-03-14 10:52:20
# from System import *
# from System.Collections.Generic import *
# from System.IO import *
# from System.Linq import *
import sys
import os


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
    def IsCommand(line)
        for (i = 0; i < len(line); i++)
            if char.IsWhiteSpace(line, i:
                continue

            if line[i] == ';':
                break

            if (line[i] == 'G') or (line[i] == 'M':
                i += 1
                if i >= len(line):
                    return False

                return char.IsDigit(line[i])

        return False

    @staticmethod
    def IsMovementCommand(command)
        for (i = 0; i < len(command); i++)
            if char.IsWhiteSpace(command, i:
                continue

            if command[i] == ';':
                break

            if command[i] == 'G':
                i += 1
                if i >= len(command):
                    return False

                if (command[i] != '0') and (command[i] != '1':
                    return False

                i += 1

                return (i >= len(command)) || char.IsWhiteSpace(command[i])

        return False


class Program:

    FirstTowerZ = 2.1
    TEMPLATE_NAME = "Retraction Test Towers Template.gcode"
    DATA_DIR = os.path.dirname(os.path.abspath(__file__))

    @staticmethod
    def GetTemplateReader():
        # formerly (nameof(RetractionTestTowersGCodeGenerator)
        # + ".Retraction Test Towers Template.gcode"))
        template_path = os.path.join(Program.DATA_DIR,
                                     Program.TEMPLATE_NAME)
        return open(template_path)

    @staticmethod
    def MeasureGCode(stream)
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
                if command.HasParameter('X':
                    x.Extend(command.GetParameter('X'))
                if command.HasParameter('Y':
                    y.Extend(command.GetParameter('Y'))

            if (command.Command == "G0") or (command.Command == "G1":
                if command.HasParameter('Z':
                    currentZ = command.GetParameter('Z')

                if command.HasParameter('E':
                    decimal e = command.GetParameter('E')

                    if (e > lastE) and (currentZ != decimal.MinValue:
                        lastE = e
                        z.Extend(currentZ)

        return (x, y, z)

    @classmethod
    def Main(cls, args)
        extents = MeasureGCode(Program.GetTemplateReader())

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
            curvePoints.Add(
                CurvePoint(
                    PointType = CurvePointType.SameValueUntil,
                    Z = FirstTowerZ,
                    Retraction = 2.0,
                )
            )

            curvePoints.Add(
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

                argName = args[index].ToLowerInvariant()

                switch (argName)
                    case "/output":
                        outputFileName = args[index + 1]
                        index += 1

                        continue
                    case "/center":
                        deltaX = decimal.Parse(args[index + 1]) - extents.X.Middle
                        deltaY = decimal.Parse(args[index + 2]) - extents.Y.Middle

                        index += 3

                        continue
                    case "/startwith":
                        initialPoint = CurvePoint()

                        initialPoint.PointType = CurvePointType.SameValueUntil
                        initialPoint.Z = FirstTowerZ
                        initialPoint.Retraction = decimal.Parse(args[index + 1])

                        curvePoints.Add(initialPoint)

                        index += 2

                        continue
                    case "/setat":
                    case "/interpolateto":
                        switch (argName)
                            case "/setat": curvePoint.PointType = CurvePointType.SameValueUntil; break
                            case "/interpolateto": curvePoint.PointType = CurvePointType.InterpolateUpTo; break

                        curvePoint.Z = decimal.Parse(args[index + 1])
                        curvePoint.Retraction = decimal.Parse(args[index + 2])

                        curvePoints.Add(curvePoint)

                        index += 3

                        continue

                    case "/checkfile":
                        AnalyzeFile(args[index + 1])

                        return

                raise Exception("Invalid command-line format")

        print("")

        if (deltaX != 0) or (deltaY != 0:
            print(
                "Will translate test print to be centred at ({0:##0.0}, {1:##0.0})",
                extents.X.Middle + deltaX,
                extents.Y.Middle + deltaY)
            print("")

        print("Z    ? Retraction")

        lastCurvePointsPassed = 0

        const decimal GraphRowHeight = 0.5m

        for (decimal z = 17.0m; z >= FirstTowerZ - GraphRowHeight; z -= GraphRowHeight)
            lastExtraRow = False

            if z < FirstTowerZ:
                lastExtraRow = True
                z = FirstTowerZ

            sys.stdout.write(z.ToString("#0.0").PadLeft(4))
            sys.stdout.write(' ')

            curvePointsPassed = curvePoints.Count(point => point.Z >= z)

            if curvePointsPassed == lastCurvePointsPassed:
                sys.stdout.write("  ")
            else:
                sys.stdout.write("+ ")
                lastCurvePointsPassed = curvePointsPassed

            retraction = GetRetractionForZ(z, curvePoints)

            sys.stdout.write(retraction.ToString("#0.0000 ").PadLeft(8))

            barWidth = (int)Math.Round(retraction * 5m)

            for (i = 0; i < barWidth; i++)
                sys.stdout.write('*')

            print("")

            if lastExtraRow:
                break

        print("")
        print("Will write output to: {0}", outputFileName)

        with open(outputFileName, 'w') as writer:
            print("")
            print("Generating G code...")

            TranslateGCode(
                GetTemplateReader(),
                writer,
                FirstTowerZ,
                deltaX,
                deltaY,
                curvePoints,
            )

        print("")
        print(Path.GetFullPath(outputFileName))

    @staticmethod
    def AnalyzeFile(fileName):
       with open(fileName, 'r') as reader:
            decimal z = decimal.MinValue
            decimal lastE = decimal.MinValue

            # CHECK NEXT LINE for type declarations !!!
            while True:
                line = stream.readline()
                if not line:
                    break
                line = line.rstrip()

                command = GCodeCommand(line)

                if (command.Command == "G0") or (command.Command == "G1":
                    if command.HasParameter('Z':
                        z = command.GetParameter('Z')

                    if command.HasParameter('E':
                        e = command.GetParameter('E')

                        if e < lastE:
                            print($"=> Retract by {lastE - e} at Z {z}")
                        else:
                            lastE = e

    @staticmethod
    def TranslateGCode(reader, writer, firstTowerZ, deltaX, deltaY, curvePoints)
        if not isinstance(firstTowerZ, float):
            raise ValueError("The firstTowerZ must be an float but"
                             " is \"{}\".".format(firstTowerZ))
        if not isinstance(curvePoints, list):
            raise ValueError("The curvePoints must be a list but"
                             " is \"{}\".".format(curvePoints))

        curvePoints.Sort(
            (left, right) => left.Z.CompareTo(right.Z))

        decimal z = decimal.MinValue

        uniqueZValues = set()

        decimal lastE = decimal.MinValue

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

            if (command.Command == "G0") or (command.Command == "G1":
                if command.HasParameter('X':
                    command.SetParameter('X', command.GetParameter('X') + deltaX)
                if command.HasParameter('Y':
                    command.SetParameter('Y', command.GetParameter('Y') + deltaY)

                if command.HasParameter('Z':
                    z = command.GetParameter('Z')

                    if uniqueZValues.Add(z:
                        sys.stdout.write('#')

                if z >= firstTowerZ:
                    if command.HasParameter('E':
                        decimal e = command.GetParameter('E')

                        if e < lastE:
                            #  Retraction!
                            numberOfRetractions += 1

                            decimal retraction = GetRetractionForZ(z, curvePoints)

                            command.SetParameter('E', lastE - retraction)

                            lcdScreenMessage = $"dE {retraction:0.000} at Z {z:#0.0}"
                            serialMessage = $"Retraction {retraction:0.00000} at Z {z:#0.0}"

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
        print("- {0} characters", gcodeWriter.NumCharactersWritten)
        print("- {0} lines", gcodeWriter.NumLines)
        print("- {0} commands", gcodeWriter.NumCommands)
        print("- {0} movement commands", gcodeWriter.NumMovementCommands)
        print("- {0} unique Z values", uniqueZValues.Count)
        print("- {0} retractions", numberOfRetractions)

    @staticmethod
    def GetRetractionForZ(z, curvePoints)
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

                decimal interpolateFrom = previousPoint.Retraction
                decimal interpolateTo = point.Retraction

                decimal interpolateFromZ = previousPoint.Z
                decimal interpolateToZ = point.Z

                decimal interpolateRange = interpolateToZ - interpolateFromZ

                decimal weightTo = (z - previousPoint.Z) / interpolateRange
                decimal weightFrom = (point.Z - z) / interpolateRange

                return interpolateFrom * weightFrom + interpolateTo * weightTo

            previousPoint = point

        return curvePoints.Last().Retraction


if __name__ == "__main__":
    Program.Main(sys.argv[1:])
