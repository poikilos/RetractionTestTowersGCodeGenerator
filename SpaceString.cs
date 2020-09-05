using System.Collections.Generic;

namespace RetractionTestTowersGCodeGenerator
{
	static class SpaceString
	{
		static Dictionary<int, string> s_cache = new Dictionary<int, string>();

		public static string OfLength(int len)
		{
			if (s_cache.TryGetValue(len, out var cachedValue))
				return cachedValue;

			return s_cache[len] = new string(' ', len);
		}
	}
}
