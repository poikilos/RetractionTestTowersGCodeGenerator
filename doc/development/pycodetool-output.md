# pycodetool output
This output is from the command shown in the first line of each code block. The home directory was redacted as `~` to be more generic.

## SpaceString.py
```
:~/git/RetractionTestTowersGCodeGenerator$ ~/git/pycodetool/pycodetool/python_remove_dotnet.py SpaceString.py SpaceString.py doc/development/pycodetool-SpaceString-identifiers.txt
I am python_remove_dotnet.py
  ignoring arg:~/git/pycodetool/pycodetool/python_remove_dotnet.py
  input file: SpaceString.py
  output file: SpaceString.py
  identifier list output file: c
  (STATUS) 12 line(s) detected

  (STATUS) preprocessing...
  (STATUS) line 3: started class SpaceString cache index [0]
  (SOURCE) line 7: source WARNING: (automatically corrected) duplicate 'OfLength' method starting on line--commenting since redundant (you may need to fix this by hand if this overload has code you needed).

  (STATUS) removing net framework...
  (CHANGE) line 3: removing 'object' inheritance since needs .net framework
  (STATUS) line 3: started class SpaceString cache index [0]
  (STATUS) save_identifier_lists...
  (STATUS) OK (save_identifier_lists to '~/git/RetractionTestTowersGCodeGenerator/doc/development/pycodetool-SpaceString-identifiers.txt')
```

## CommandCache.py
```
:~/git/RetractionTestTowersGCodeGenerator$ ~/git/pycodetool/pycodetool/python_remove_dotnet.py CommandCache.py CommandCache.py doc/development/pycodetool-CommandCache-identifiers.txt
I am python_remove_dotnet.py
  ignoring arg:~/git/pycodetool/pycodetool/python_remove_dotnet.py
  input file: CommandCache.py
  output file: CommandCache.py
  identifier list output file: c
  (STATUS) 6 line(s) detected

  (STATUS) preprocessing...
  (STATUS) line 5: started class CommandCache cache index [0]
  (SOURCE) line 6: (source error preprocessing) expected '=' then value after class member

  (STATUS) removing net framework...
  (CHANGE) line 2: commenting useless line since imports framework
  (CHANGE) line 3: commenting useless line since imports framework
  (CHANGE) line 5: removing 'object' inheritance since needs .net framework
  (STATUS) line 5: started class CommandCache cache index [0]
  (SOURCE) line 6: (source error removing net framework) expected '=' then value after class member
  (STATUS) save_identifier_lists...
  (STATUS) OK (save_identifier_lists to '~/git/RetractionTestTowersGCodeGenerator/doc/development/pycodetool-CommandCache-identifiers.txt')
```


## GCodeCommand.py
```
:~/git/RetractionTestTowersGCodeGenerator$ ~/git/pycodetool/pycodetool/python_remove_dotnet.py GCodeCommand.py GCodeCommand.py doc/development/pycodetool-GCodeCommand-identifiers.txt
I am python_remove_dotnet.py
  ignoring arg:~/git/pycodetool/pycodetool/python_remove_dotnet.py
  input file: GCodeCommand.py
  output file: GCodeCommand.py
  identifier list output file: c
  (STATUS) 30 line(s) detected

  (STATUS) preprocessing...
  (STATUS) line 6: started class GCodeCommand cache index [0]
  (SOURCE) line 15: source WARNING: (automatically corrected) duplicate 'ToString' method starting on line--commenting since redundant (you may need to fix this by hand if this overload has code you needed).
  (SOURCE) line 23: source WARNING: (automatically corrected) duplicate 'WriteTo' method starting on line--commenting since redundant (you may need to fix this by hand if this overload has code you needed).
  (SOURCE) line 29: source WARNING: (automatically corrected) duplicate 'HasParameter' method starting on line--commenting since redundant (you may need to fix this by hand if this overload has code you needed).

  (STATUS) removing net framework...
  (CHANGE) line 2: commenting useless line since imports framework
  (CHANGE) line 3: commenting useless line since imports framework
  (CHANGE) line 4: commenting useless line since imports framework
  (CHANGE) line 6: removing 'object' inheritance since needs .net framework
  (STATUS) line 6: started class GCodeCommand cache index [0]
  (CHANGE) line 10: (changing) using ' is not None' instead of ' != None'
  (STATUS) save_identifier_lists...
  (STATUS) OK (save_identifier_lists to '~/git/RetractionTestTowersGCodeGenerator/doc/development/pycodetool-GCodeCommand-identifiers.txt')
```


## GCodeCommandPart.py
```
:~/git/RetractionTestTowersGCodeGenerator$ ~/git/pycodetool/pycodetool/python_remove_dotnet.py GCodeCommandPart.py GCodeCommandPart.py doc/development/pycodetool-GCodeCommandPart-identifiers.txt
I am python_remove_dotnet.py
  ignoring arg:~/git/pycodetool/pycodetool/python_remove_dotnet.py
  input file: GCodeCommandPart.py
  output file: GCodeCommandPart.py
  identifier list output file: c
  (STATUS) 64 line(s) detected

  (STATUS) preprocessing...
  (STATUS) line 6: started class GCodeCommandPart cache index [0]
  (SOURCE) line 9: source WARNING: (automatically corrected) duplicate 'ToString' method starting on line--commenting since redundant (you may need to fix this by hand if this overload has code you needed).
  (SOURCE) line 21: source WARNING: (automatically corrected) duplicate 'WriteTo' method starting on line--commenting since redundant (you may need to fix this by hand if this overload has code you needed).
  (SOURCE) line 33: source WARNING: (automatically corrected) duplicate 'ParseStringToParts' method starting on line--commenting since redundant (you may need to fix this by hand if this overload has code you needed).

  (STATUS) removing net framework...
  (CHANGE) line 2: commenting useless line since imports framework
  (CHANGE) line 3: commenting useless line since imports framework
  (CHANGE) line 4: commenting useless line since imports framework
  (CHANGE) line 6: removing 'object' inheritance since needs .net framework
  (STATUS) line 6: started class GCodeCommandPart cache index [0]
  (STATUS) save_identifier_lists...
  (STATUS) OK (save_identifier_lists to '~/git/RetractionTestTowersGCodeGenerator/doc/development/pycodetool-GCodeCommandPart-identifiers.txt')
```

## GCodeCommandPartType.py
```
:~/git/RetractionTestTowersGCodeGenerator$ ~/git/pycodetool/pycodetool/python_remove_dotnet.py GCodeCommandPartType.py GCodeCommandPartType.py doc/development/pycodetool-GCodeCommandPartType-identifiers.txt
I am python_remove_dotnet.py
  ignoring arg:~/git/pycodetool/pycodetool/python_remove_dotnet.py
  input file: GCodeCommandPartType.py
  output file: GCodeCommandPartType.py
  identifier list output file: c
  (STATUS) 2 line(s) detected

  (STATUS) preprocessing...

  (STATUS) removing net framework...
  (STATUS) save_identifier_lists...
  (STATUS) OK (save_identifier_lists to '~/git/RetractionTestTowersGCodeGenerator/doc/development/pycodetool-GCodeCommandPartType-identifiers.txt')
```


## Program.py
```
:~/git/RetractionTestTowersGCodeGenerator$ ~/git/pycodetool/pycodetool/python_remove_dotnet.py Program.py Program.py doc/development/pycodetool-Program-identifiers.txtI am python_remove_dotnet.py
  ignoring arg:~/git/pycodetool/pycodetool/python_remove_dotnet.py
  input file: Program.py
  output file: Program.py
  identifier list output file: c
  (STATUS) 19 line(s) detected

  (STATUS) preprocessing...
  (STATUS) line 6: started class Program cache index [0]
  (SOURCE) line 10: (source error preprocessing) expected '=' then value after class member
  (STATUS) line 10: started class CurvePointType cache index [1]
  (SOURCE) line 11: source WARNING: (automatically corrected) duplicate '__init__' method starting on line--commenting since redundant (you may need to fix this by hand if this overload has code you needed).
  (STATUS) line 13: -->ended class CurvePointType (near '    class CurvePoint(object):')
  (STATUS) line 13: started class CurvePoint cache index [2]
  (SOURCE) line 14: source WARNING: (automatically corrected) duplicate '__init__' method starting on line--commenting since redundant (you may need to fix this by hand if this overload has code you needed).
  (STATUS) line 16: -->ended class CurvePoint (near '    def GetTemplateReader():')
  (SOURCE) line 16: source WARNING: (automatically corrected) duplicate 'GetTemplateReader' method starting on line--commenting since redundant (you may need to fix this by hand if this overload has code you needed).

  (STATUS) removing net framework...
  (CHANGE) line 2: commenting useless line since imports framework
  (CHANGE) line 3: commenting useless line since imports framework
  (CHANGE) line 4: commenting useless line since imports framework
  (CHANGE) line 6: removing 'object' inheritance since needs .net framework
  (STATUS) line 6: started class Program cache index [0]
  (SOURCE) line 10: (source error removing net framework) expected '=' then value after class member
  (CHANGE) line 10: removing 'object' inheritance since needs .net framework
  (STATUS) line 10: started class CurvePointType cache index [1]
  (STATUS) line 13: -->ended class CurvePointType (near '    class CurvePoint(object):')
  (CHANGE) line 13: removing 'object' inheritance since needs .net framework
  (STATUS) line 13: started class CurvePoint cache index [2]
  (STATUS) line 19: -->ended class CurvePoint (near '    GetTemplateReader = staticmethod(GetTemplateReader)')
  (STATUS) save_identifier_lists...
  (STATUS) OK (save_identifier_lists to '~/git/RetractionTestTowersGCodeGenerator/doc/development/pycodetool-Program-identifiers.txt')
```
