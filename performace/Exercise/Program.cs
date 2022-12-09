var results = GetCharacterCount("John Doe");
foreach( KeyValuePair<char, int> kvp in results )
{
    Console.WriteLine("'{0}':{1}", kvp.Key, kvp.Value);
}

IDictionary<char, int> GetCharacterCount(string name)
{
    var result = new Dictionary<char, int>();
    foreach (char c in name)
    {
        result[c] = 1;
    }
    return result;
}