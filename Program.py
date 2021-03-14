#!/usr/bin/env python
# Processed by pycodetool https://github.com/poikilos/pycodetool
# 2021-03-14 10:52:20
# from System import *
# from System.Collections.Generic import *
# from System.IO import *
# from System.Linq import *
import sys
import os

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
                             " is \"{}\".".format(commandNumber))
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
    def __init__(self):
        self.PointType = None
        self.Z = None
        self.Retraction = None


class Program:
    FirstTowerZ = 2.1;
    TEMPLATE_NAME = "Retraction Test Towers Template.gcode"
    DATA_DIR = os.path.dirname(os.path.abspath(__file__))

    def __init__(self):
        pass

    @staticmethod
    def GetTemplateReader():
        # formerly (nameof(RetractionTestTowersGCodeGenerator)
        # + ".Retraction Test Towers Template.gcode"))

        template_path = os.path.join(Program.DATA_DIR,
                                     Program.TEMPLATE_NAME)
        return open(template_path)

    def MeasureGCode(stream):
        result = [0, 0, 0]
        raise NotImplementedError("MeasureGCode")
        return result
