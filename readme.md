# RetractionTowerProcessor

Generate retraction test towers by varying retraction by z in G-code.

This is Poikilos' Python fork of logiclrd's C# tool (RetractionTestTowersGCodeGenerator).

Sourcecode: https://github.com/poikilos/RetractionTowerProcessor

You can calibrate further using my related projects:
- [TemperatureTowerProcessor](https://github.com/poikilos/TemperatureTowerProcessor)
- [LinearAdvanceTowerGenerator](https://github.com/poikilos/LinearAdvanceTowerGenerator)


## Differences in Poikilos' Python fork
- Change to a new more stable tower to facilitate many levels.
  - The base is still 25x10x2 (but not for the "arches" version--see [Alternate towers](#alternate-towers)).


## Measurements

### Cura
Cura places it at the center and changes the origin to the center.
Therefore:
- To center the corner, set the position to 12.5,5
- To move the corner of a model to a given point:
  - Place the corner at 0,0 by subtracting 102.5,102.5 (or whatever is half of your bed size) from the numbers above but flip the sign of y afterward (in this case, set the coords to -90,97.5)
    - For CR-10, subtract 150,150 then flip y resulting in -137.5,145
  - Now take that position and add the position you want. For testing purposes only (or if you have a very large bed) to match the example G-code your desired position for the corner would be 182.7,190.2 but subtract in the case of y (in this case (-90+182.7),(97.5-190.2) and the result is 92.7,-92.7)
    - For CR-10, do (-137.5+182.7),(145-190.2) and the result is 45.2,-45.2
  - The example gcode uses:
    - layer height: .1
    - first layer height: .3
    - retraction 3 (Cura's default is 5)
    - retraction speed 40 (Cura's default is 45)
    - for other settings, see tests/data


## Development
### Alternate towers
The "arches" version has discreet levels:
- It has a 25x25x5 mm base.
- The code accounts for the extents automatically (See `cls.MeasureGCode(reader)`) but not the base height (and not top?).
- levels: 5 (height of the base; Use the `/setat 5` option to account for this), 15, 25, 35, 45, 55, 65 (top of highest level)
