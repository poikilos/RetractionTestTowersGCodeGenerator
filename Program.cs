using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;

namespace RetractionTestTowersGCodeGenerator
{
	class Program
	{
		enum CurvePointType
		{
			SameValueUntil,
			InterpolateUpTo,
		}

		class CurvePoint
		{
			public CurvePointType PointType;
			public decimal Z;
			public decimal Retraction;
		}

		const decimal FirstTowerZ = 2.1m;

		static TextReader GetTemplateReader()
			=> new StreamReader(typeof(Program).Assembly.GetManifestResourceStream(nameof(RetractionTestTowersGCodeGenerator) + ".Retraction Test Towers Template.gcode"));

		struct Extent
		{
			public decimal From;
			public decimal To;

			public decimal Middle => From * 0.5m + To * 0.5m;

			public void Extend(decimal value)
			{
				if (value < From)
					From = value;
				if (value > To)
					To = value;
			}
		}

		static (Extent X, Extent Y, Extent Z) MeasureGCode(TextReader stream)
		{
			// Count only G1 moves in X and Y.
			// Count G0 and G1 moves in Z, but only for Z values where filament is extruded.
			Extent x, y, z;

			x.From = y.From = z.From = decimal.MaxValue;
			x.To = y.To = z.To = decimal.MinValue;

			decimal lastE = decimal.MinValue;
			decimal currentZ = decimal.MinValue;

			while (true)
			{
				string line = stream.ReadLine();

				if (line == null)
					break;

				if (string.IsNullOrWhiteSpace(line))
					continue;

				var command = new GCodeCommand(line);

				if (command.Command == "G1")
				{
					if (command.HasParameter('X'))
						x.Extend(command.GetParameter('X'));
					if (command.HasParameter('Y'))
						y.Extend(command.GetParameter('Y'));
				}

				if ((command.Command == "G0") || (command.Command == "G1"))
				{
					if (command.HasParameter('Z'))
						currentZ = command.GetParameter('Z');

					if (command.HasParameter('E'))
					{
						decimal e = command.GetParameter('E');

						if ((e > lastE) && (currentZ != decimal.MinValue))
						{
							lastE = e;
							z.Extend(currentZ);
						}
					}
				}
			}

			return (x, y, z);
		}

		static void Main(string[] args)
		{
			var extents = MeasureGCode(GetTemplateReader());

			Console.WriteLine("Template extents:");

			Console.WriteLine("    From     Centre   To");
			Console.WriteLine("X   {0,5:##0.0}    {1,5:##0.0}    {2,5:##0.0}", extents.X.From, extents.X.Middle, extents.X.To);
			Console.WriteLine("Y   {0,5:##0.0}    {1,5:##0.0}    {2,5:##0.0}", extents.Y.From, extents.Y.Middle, extents.Y.To);
			Console.WriteLine("Z   {0,5:##0.0}    {1,5:##0.0}    {2,5:##0.0}", extents.Z.From, extents.Z.Middle, extents.Z.To);

			List<CurvePoint> curvePoints = new List<CurvePoint>();

			decimal deltaX = 0.0m;
			decimal deltaY = 0.0m;

			string outputFileName = "RetractionTest.gcode";

			if (args.Length == 0)
			{
				curvePoints.Add(
					new CurvePoint()
					{
						PointType = CurvePointType.SameValueUntil,
						Z = FirstTowerZ,
						Retraction = 2m,
					});

				curvePoints.Add(
					new CurvePoint()
					{
						PointType = CurvePointType.InterpolateUpTo,
						Z = extents.Z.To,
						Retraction = 3m,
					});
			}
			else
			{
				int index = 0;

				while (index < args.Length)
				{
					CurvePoint curvePoint = new CurvePoint();

					string argName = args[index].ToLowerInvariant();

					switch (argName)
					{
						case "/output":
						{
							outputFileName = args[index + 1];
							index++;

							continue;
						}
						case "/center":
						{
							deltaX = decimal.Parse(args[index + 1]) - extents.X.Middle;
							deltaY = decimal.Parse(args[index + 2]) - extents.Y.Middle;

							index += 3;

							continue;
						}
						case "/startwith":
						{
							var initialPoint = new CurvePoint();

							initialPoint.PointType = CurvePointType.SameValueUntil;
							initialPoint.Z = FirstTowerZ;
							initialPoint.Retraction = decimal.Parse(args[index + 1]);

							curvePoints.Add(initialPoint);

							index += 2;

							continue;
						}
						case "/setat":
						case "/interpolateto":
						{
							switch (argName)
							{
								case "/setat": curvePoint.PointType = CurvePointType.SameValueUntil; break;
								case "/interpolateto": curvePoint.PointType = CurvePointType.InterpolateUpTo; break;
							}

							curvePoint.Z = decimal.Parse(args[index + 1]);
							curvePoint.Retraction = decimal.Parse(args[index + 2]);

							curvePoints.Add(curvePoint);

							index += 3;

							continue;
						}

						case "/checkfile":
						{
							AnalyzeFile(args[index + 1]);

							return;
						}
					}

					throw new Exception("Invalid command-line format");
				}
			}

			Console.WriteLine();

			if ((deltaX != 0) || (deltaY != 0))
			{
				Console.WriteLine(
					"Will translate test print to be centred at ({0:##0.0}, {1:##0.0})",
					extents.X.Middle + deltaX,
					extents.Y.Middle + deltaY);
				Console.WriteLine();
			}

			Console.WriteLine("Z    ? Retraction");

			int lastCurvePointsPassed = 0;

			const decimal GraphRowHeight = 0.5m;

			for (decimal z = 17.0m; z >= FirstTowerZ - GraphRowHeight; z -= GraphRowHeight)
			{
				bool lastExtraRow = false;

				if (z < FirstTowerZ)
				{
					lastExtraRow = true;
					z = FirstTowerZ;
				}

				Console.Write(z.ToString("#0.0").PadLeft(4));
				Console.Write(' ');

				int curvePointsPassed = curvePoints.Count(point => point.Z >= z);

				if (curvePointsPassed == lastCurvePointsPassed)
					Console.Write("  ");
				else
				{
					Console.Write("+ ");
					lastCurvePointsPassed = curvePointsPassed;
				}

				var retraction = GetRetractionForZ(z, curvePoints);

				Console.Write(retraction.ToString("#0.0000 ").PadLeft(8));

				int barWidth = (int)Math.Round(retraction * 5m);

				for (int i = 0; i < barWidth; i++)
					Console.Write('*');

				Console.WriteLine();

				if (lastExtraRow)
					break;
			}

			Console.WriteLine();
			Console.WriteLine("Will write output to: {0}", outputFileName);

			using (var writer = new StreamWriter(outputFileName))
			{
				Console.WriteLine();
				Console.WriteLine("Generating G code...");

				TranslateGCode(
					GetTemplateReader(),
					writer,
					FirstTowerZ,
					deltaX,
					deltaY,
					curvePoints);
			}

			Console.WriteLine();
			Console.WriteLine(Path.GetFullPath(outputFileName));
		}

		private static void AnalyzeFile(string fileName)
		{
			using (var reader = new StreamReader(fileName))
			{
				decimal z = decimal.MinValue;
				decimal lastE = decimal.MinValue;

				while (true)
				{
					string line = reader.ReadLine();

					if (line == null)
						break;

					var command = new GCodeCommand(line);

					if ((command.Command == "G0") || (command.Command == "G1"))
					{
						if (command.HasParameter('Z'))
							z = command.GetParameter('Z');

						if (command.HasParameter('E'))
						{
							var e = command.GetParameter('E');

							if (e < lastE)
								Console.WriteLine($"=> Retract by {lastE - e} at Z {z}");
							else
								lastE = e;
						}
					}
				}
			}
		}

		class GCodeWriter
		{
			TextWriter _underlying;

			public int NumLines = 0;
			public int NumCommands = 0;
			public int NumMovementCommands = 0;
			public int NumCharactersWritten = 0;

			public GCodeWriter(TextWriter underlying)
			{
				_underlying = underlying;
			}

			public void WriteLine(string command)
			{
				NumLines++;
				if (IsCommand(command))
				{
					NumCommands++;

					if (IsMovementCommand(command))
						NumMovementCommands++;
				}
				NumCharactersWritten += command.Length + _underlying.NewLine.Length;

				_underlying.WriteLine(command);
			}

			public void WriteLine(GCodeCommand command)
				=> WriteLine(command.ToString());

			static bool IsCommand(string line)
			{
				for (int i = 0; i < line.Length; i++)
				{
					if (char.IsWhiteSpace(line, i))
						continue;

					if (line[i] == ';')
						break;

					if ((line[i] == 'G') || (line[i] == 'M'))
					{
						i++;
						if (i >= line.Length)
							return false;

						return char.IsDigit(line[i]);
					}
				}

				return false;
			}

			static bool IsMovementCommand(string command)
			{
				for (int i = 0; i < command.Length; i++)
				{
					if (char.IsWhiteSpace(command, i))
						continue;

					if (command[i] == ';')
						break;

					if (command[i] == 'G')
					{
						i++;
						if (i >= command.Length)
							return false;

						if ((command[i] != '0') && (command[i] != '1'))
							return false;

						i++;

						return (i >= command.Length) || char.IsWhiteSpace(command[i]);
					}
				}

				return false;
			}
		}

		static void TranslateGCode(TextReader reader, TextWriter writer, decimal firstTowerZ, decimal deltaX, decimal deltaY, List<CurvePoint> curvePoints)
		{
			curvePoints.Sort(
				(left, right) => left.Z.CompareTo(right.Z));

			decimal z = decimal.MinValue;

			var uniqueZValues = new HashSet<decimal>();

			decimal lastE = decimal.MinValue;

			string lastSerialMessage = "";

			var gcodeWriter = new GCodeWriter(writer);

			int numberOfRetractions = 0;

			while (true)
			{
				string line = reader.ReadLine();

				if (line == null)
					break;

				var command = new GCodeCommand(line);

				if ((command.Command == "G0") || (command.Command == "G1"))
				{
					if (command.HasParameter('X'))
						command.SetParameter('X', command.GetParameter('X') + deltaX);
					if (command.HasParameter('Y'))
						command.SetParameter('Y', command.GetParameter('Y') + deltaY);

					if (command.HasParameter('Z'))
					{
						z = command.GetParameter('Z');

						if (uniqueZValues.Add(z))
							Console.Write('#');
					}

					if (z >= firstTowerZ)
					{
						if (command.HasParameter('E'))
						{
							decimal e = command.GetParameter('E');

							if (e < lastE)
							{
								// Retraction!
								numberOfRetractions++;

								decimal retraction = GetRetractionForZ(z, curvePoints);

								command.SetParameter('E', lastE - retraction);

								string lcdScreenMessage = $"dE {retraction:0.000} at Z {z:#0.0}";
								string serialMessage = $"Retraction {retraction:0.00000} at Z {z:#0.0}";

								gcodeWriter.WriteLine("M117 " + lcdScreenMessage);

								if (serialMessage != lastSerialMessage)
								{
									gcodeWriter.WriteLine("M118 " + serialMessage);

									lastSerialMessage = serialMessage;
								}
							}

							lastE = e;
						}
					}
				}

				gcodeWriter.WriteLine(command);
			}

			gcodeWriter.WriteLine("G0 X0 Y0");

			Console.WriteLine();
			Console.WriteLine();
			Console.WriteLine("Output:");
			Console.WriteLine("- {0} characters", gcodeWriter.NumCharactersWritten);
			Console.WriteLine("- {0} lines", gcodeWriter.NumLines);
			Console.WriteLine("- {0} commands", gcodeWriter.NumCommands);
			Console.WriteLine("- {0} movement commands", gcodeWriter.NumMovementCommands);
			Console.WriteLine("- {0} unique Z values", uniqueZValues.Count);
			Console.WriteLine("- {0} retractions", numberOfRetractions);
		}

		static decimal GetRetractionForZ(decimal z, List<CurvePoint> curvePoints)
		{
			CurvePoint previousPoint = curvePoints[0];

			foreach (var point in curvePoints)
			{
				if (point.Z >= z)
				{
					if (point.PointType == CurvePointType.SameValueUntil)
						return previousPoint.Retraction;

					decimal interpolateFrom = previousPoint.Retraction;
					decimal interpolateTo = point.Retraction;

					decimal interpolateFromZ = previousPoint.Z;
					decimal interpolateToZ = point.Z;

					decimal interpolateRange = interpolateToZ - interpolateFromZ;

					decimal weightTo = (z - previousPoint.Z) / interpolateRange;
					decimal weightFrom = (point.Z - z) / interpolateRange;

					return interpolateFrom * weightFrom + interpolateTo * weightTo;
				}

				previousPoint = point;
			}

			return curvePoints.Last().Retraction;
		}
	}
}
