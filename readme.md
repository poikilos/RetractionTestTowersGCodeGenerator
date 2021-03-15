# RetractionTowerProcessor

Generate retraction test towers by varying retraction by z in G-code.

This is Poikilos' Python fork of logiclrd's C# tool (RetractionTestTowersGCodeGenerator).


## Measurements
The test is 25x10 mm.

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
