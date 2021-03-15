#!/usr/bin/env python

from GCodeCommandPart import (
    GCodeCommandPart,
    IsSpace,
)

from GCodeCommand import (
    GCodeCommand,
)

from Program import (
    Extent,
    CurvePoint,
    CurvePointType,
)

def toPythonLiteral(v):
    '''
    [copied from pycodetool by author]
    '''
    if v is None:
        return None
    elif v is False:
        return "False"
    elif v is True:
        return "True"
    elif ((type(v) == int) or (type(v) == float)):
        return str(v)
    elif (type(v) == tuple) or (type(v) == list):
        enclosures = '()'
        if type(v) == list:
            enclosures = '[]'
        s = enclosures[0]
        for val in v:
            s += toPythonLiteral(val) + ", "
            # ^ Ending with an extra comma has no effect on length.
        s += enclosures[1]
        return s
    return "'{}'".format(
        v.replace("'", "\\'").replace("\r", "\\r").replace("\n", "\\n")
    )


def assertEqual(v1, v2, tbs=None):
    '''
    [copied from pycodetool by author]
    Show the values if they differ before the assertion error stops the
    program.

    Keyword arguments:
    tbs -- traceback string (either caller or some sort of message to
           show to describe what data produced the arguments if they're
           derived from something else)
    '''
    if ((v1 is True) or (v2 is True) or (v1 is False) or (v2 is False)
            or (v1 is None) or (v2 is None)):
        if v1 is not v2:
            print("")
            print("{} is not {}".format(toPythonLiteral(v1),
                                        toPythonLiteral(v2)))
            if tbs is not None:
                print("for {}".format(tbs))
        assert(v1 is v2)
    else:
        if v1 != v2:
            print("")
            print("{} != {}".format(toPythonLiteral(v1),
                                    toPythonLiteral(v2)))
            if tbs is not None:
                print("while {}".format(tbs))
        assert(v1 == v2)


def assertAllEqual(list1, list2, tbs=None):
    '''
    [copied from pycodetool by author]
    '''
    if len(list1) != len(list2):
        print("The lists are not the same length: list1={}"
              " and list2={}".format(list1, list2))
        assertEqual(len(list1), len(list2))
    for i in range(len(list1)):
        assertEqual(list1[i], list2[i], tbs=tbs)

def assertMembersEqual(v1, v2, members, tbs=None):
    for member in members:
        if getattr(v1, member) != getattr(v2, member):
            print("")
            print("{} != {}"
                  "".format(getattr(v1, member), getattr(v2, member)))
            if tbs is not None:
                print("while {}".format(tbs))
        assert(getattr(v1, member) == getattr(v2, member))

def assertPartEqual(v1, v2, tbs=None):
    '''
    Show the values if they differ before the assertion error stops the
    program.

    Keyword arguments:
    tbs -- traceback string (either caller or some sort of message to
           show to describe what data produced the arguments if they're
           derived from something else)
    '''
    members = []
    assertMembersEqual(v1, v2, members, tbs=tbs)

def assertPartsAllEqual(list1, list2, tbs=None):
    if len(list1) != len(list2):
        print("The lists are not the same length: list1={}"
              " and list2={}".format(list1, list2))
        assertEqual(len(list1), len(list2))
    for i in range(len(list1)):
        assertPartEqual(list1[i], list2[i], tbs=tbs)


assert(IsSpace(" "))
assert(not IsSpace(" a"))
assert(not IsSpace("a "))
assert(not IsSpace(" a "))
assert(IsSpace("a ", 1))
assert(IsSpace(" a", 0))
assert(IsSpace(" a ", 2))

good_parts = [GCodeCommandPart(Character="M", Number=70)]
got_parts = []
# i = -1
for part in GCodeCommandPart.ParseStringToParts("M70"):
    got_parts.append(part)
    # i += 1
    # assertEqual(part, good_parts[i])
assertPartsAllEqual(good_parts, got_parts)
assertEqual(got_parts[0].ToString(), "M70")

assertEqual(GCodeCommand("M70").ToString(), "M70")

line = "G00 X25 Y20"
command = GCodeCommand(line)
assertEqual(command.Command, "G0")
# ^ "[you don't need leading zeroes](https://www.cnctrainingcentre.com/
# beginners/cnc-programming-basics-leading-ttrailing-zeros/)."
# <https://www.cnctrainingcentre.com/fanuc-turn/g01-g00-basic-cnc-
# programming/>
assertEqual(command.GetParameter('G'), 0)
assert(isinstance(command.GetParameter('G'), int))
assert(isinstance(command.GetParameter('X'), float))
# ^ Even if there is no decimal, it should be converted to float.
assertEqual(command.GetParameter('X'), 25)
assertEqual(command.GetParameter('Y'), 20)

line="G1 X206.867 Y199.367 E294.62339"
command = GCodeCommand(line)
assertEqual(command.Command, "G1")
assert(isinstance(command.GetParameter('G'), int))
assert(isinstance(command.GetParameter('X'), float))
assertEqual(command.GetParameter('X'), 206.867)
assertEqual(command.GetParameter('E'), 294.62339)

ex = Extent()
ex.From = 1.0
ex.To = 3.0
assertEqual(ex.Middle, 2.0)
ex.Extend(0.0)
assertEqual(ex.Middle, 1.5)
ex.Extend(5.0)
assertEqual(ex.Middle, 2.5)

curvePoints = []
curvePoints.append(
    CurvePoint(
        PointType = CurvePointType.SameValueUntil,
        Z = 3.0,
        Retraction = 2.0,
    )
)
curvePoints.append(
    CurvePoint(
        PointType = CurvePointType.SameValueUntil,
        Z = 1.0,
        Retraction = 3.0,
    )
)
curvePoints.append(
    CurvePoint(
        PointType = CurvePointType.SameValueUntil,
        Z = 2.0,
        Retraction = 1.0,
    )
)
curvePoints = sorted(curvePoints)
assertEqual(curvePoints[0].Z, 1.0)
assertEqual(curvePoints[1].Z, 2.0)
assertEqual(curvePoints[2].Z, 3.0)


lastE = 3
e = 1
z = .32
'''
s = "=> Retract by {lastE - e} at Z {z}".format(
    lastE=lastE,
    z=z,
    e=e,
)
'''
# ^ C#-like operations don't work
s = "=> Retract by {0} at Z {z}".format(
    lastE - e,
    z=z,
)
assertEqual(s, "=> Retract by "+str(lastE-e)+" at Z "+str(z))

z = 1.5
curvePointsPassed = \
    sum(1 for point in curvePoints if point.Z >= z)
assertEqual(curvePointsPassed, 2)

z = -1
curvePointsPassed = \
    sum(1 for point in curvePoints if point.Z >= z)
assertEqual(curvePointsPassed, 3)

z = 3.0
curvePointsPassed = \
    sum(1 for point in curvePoints if point.Z >= z)
assertEqual(curvePointsPassed, 1)

print("All tests passed.")
