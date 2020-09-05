using System;
using System.IO;
using System.Linq;
using System.Text;

namespace RetractionTestTowersGCodeGenerator
{
	class GCodeCommand
	{
		public string Command;

		public char CommandType;
		public int CommandNumber;

		public GCodeCommand(string line)
		{
			_parts = GCodeCommandPart.ParseStringToParts(line).ToArray();

			var firstPart = _parts.FirstOrDefault(part => part.Type == GCodeCommandPartType.CharacterAndNumber);

			if (firstPart != null)
			{
				CommandType = firstPart.Character;
				CommandNumber = (int)firstPart.Number;

				Command = CommandCache.Get(CommandType, CommandNumber);
			}
		}

		public override string ToString()
		{
			var builder = new StringBuilder();

			foreach (var part in _parts)
				builder.Append(part);

			return builder.ToString();
		}

		public void WriteTo(TextWriter writer)
		{
			foreach (var part in _parts)
				part.WriteTo(writer);
		}

		public bool HasParameter(char v)
			=> GetPartByCharacter(v) != null;

		public decimal GetParameter(char param)
		{
			var part = GetPartByCharacter(param);

			if (part == null)
				throw new Exception("Command does not have a parameter '" + param + "'");

			return part.Number;
		}

		public void SetParameter(char param, decimal value)
		{
			var part = GetPartByCharacter(param);

			if (part == null)
				throw new Exception("Command does not have a parameter '" + param + "'");

			part.Number = value;
		}

		GCodeCommandPart GetPartByCharacter(char param)
			=> _parts.FirstOrDefault(part => (part.Type == GCodeCommandPartType.CharacterAndNumber) && (part.Character == param));

		GCodeCommandPart[] _parts;
	}
}
