using System;
using System.Collections.Generic;
using System.Text;

namespace RetractionTestTowersGCodeGenerator
{
	static class CommandCache
	{
		static Dictionary<(char, int), string> s_cache = new Dictionary<(char, int), string>();

		public static string Get(char commandType, int commandNumber)
		{
			var key = (commandType, commandNumber);

			if (s_cache.TryGetValue(key, out var cached))
				return cached;

			return s_cache[key] = new StringBuilder(capacity: 4).Append(commandType).Append(commandNumber).ToString();
		}
	}
}
