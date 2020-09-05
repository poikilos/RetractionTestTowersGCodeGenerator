using System;
using System.Collections.Generic;
using System.IO;
using System.Text;

namespace RetractionTestTowersGCodeGenerator
{
	class GCodeCommandPart
	{
		public GCodeCommandPartType Type;
		public char Character;
		public decimal Number;
		public string Text;

		public override string ToString()
		{
			switch (Type)
			{
				case GCodeCommandPartType.Space:
					return SpaceString.OfLength((int)Number);
				case GCodeCommandPartType.CharacterAndNumber:
					return new StringBuilder(capacity: 6).Append(Character).Append(Number).ToString();
				case GCodeCommandPartType.Comment:
					return ';' + Text;
				case GCodeCommandPartType.Text:
					return Text;

				default: throw new Exception("Internal error");
			}
		}

		public void WriteTo(TextWriter writer)
		{
			switch (Type)
			{
				case GCodeCommandPartType.Space:
					writer.Write(SpaceString.OfLength((int)Number));
					break;
				case GCodeCommandPartType.CharacterAndNumber:
					writer.Write(Character);
					writer.Write(Number.ToString("##0.#####"));
					break;
				case GCodeCommandPartType.Comment:
					writer.Write(';');
					writer.Write(Text);
					break;

				default: throw new Exception("Internal error");
			}
		}

		public static IEnumerable<GCodeCommandPart> ParseStringToParts(string line)
		{
			bool isFirstPart = true;
			int index = 0;

			while (index < line.Length)
			{
				if (line[index] == ';')
				{
					yield return
						new GCodeCommandPart()
						{
							Type = GCodeCommandPartType.Comment,
							Text = line.Substring(index + 1),
						};

					yield break;
				}

				if (char.IsWhiteSpace(line[index]))
				{
					int count = 1;
					index++;

					while ((index < line.Length) && char.IsWhiteSpace(line, index))
					{
						count++;
						index++;
					}

					yield return
						new GCodeCommandPart()
						{
							Type = GCodeCommandPartType.Space,
							Number = count,
						};
				}
				else
				{
					GCodeCommandPart part = new GCodeCommandPart();

					part.Type = GCodeCommandPartType.CharacterAndNumber;
					part.Character = line[index];

					index++;

					int numberStart = index;

					while ((index < line.Length) && !char.IsWhiteSpace(line, index))
						index++;

					part.Number = decimal.Parse(line.Substring(numberStart, index - numberStart));

					yield return part;

					bool wasFirstPart = isFirstPart;

					isFirstPart = false;

					if (wasFirstPart
					 && (part.Character == 'M')
					 && ((part.Number == 117m) || (part.Number == 118m))
					 && (index < line.Length))
					{
						// Return remainder of line as a single text block
						int count = 1;
						index++;

						while ((index < line.Length) && char.IsWhiteSpace(line, index))
						{
							count++;
							index++;
						}

						yield return
							new GCodeCommandPart()
							{
								Type = GCodeCommandPartType.Space,
								Number = count,
							};

						if (index < line.Length)
						{
							yield return
								new GCodeCommandPart()
								{
									Type = GCodeCommandPartType.Text,
									Text = line.Substring(index),
								};
						}

						yield break;
					}
				}
			}
		}
	}
}
