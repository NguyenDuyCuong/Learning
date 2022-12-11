using System;
using System.Collections;
using System.Collections.Generic;
using System.Text;

var results = GetCharacterCount("John Doe");
foreach( KeyValuePair<char, int> kvp in results )
{
    Console.WriteLine("'{0}':{1}", kvp.Key, kvp.Value);
}

Console.WriteLine(ReplaceDigits("4 score and 7 years ago, 8 men had the same PIN code: 6571"));

Matrix A = new Matrix(new int[,] { { 1, 2, 3 }, { 4, 5, 6 } });
Matrix B = new Matrix(new int[,] { { 7, 8 }, { 9, 10 }, { 11, 12 } });
Matrix C = Multiply(A, B);

Console.WriteLine(C[0,0]);


//Return character counts in a given input string
//Write a method GetCharacterCount in the class Exercise that expects a string parameter called name and does the following:

//For every unique character in the name, count how many times that character occurs in the name. Return a dictionary with each unique character in the name as key, and the count of how many times that character appears in the name as the value. Ignore spaces and treat all characters as lower case

//So for the input string "John Doe", I expect the following output:

//'j':1
//'o':2
//'h':1
//'n':1
//'d':1
//'e':1

//Requirements: your code _cannot_ use boxing or unboxing. 

//The exercise.cs file contains one or more errors. It returns invalid output, but it also introduces boxing and unboxing in the compiled code. Your task is to remove all errors. Make sure you return the correct output, and ensure that the compiler will not introduce BOX or UNBOX operations anywhere. 
IDictionary<char, int> GetCharacterCount(string name)
{
    var result = new Dictionary<char, int>();
    for (int i = 0; i < name.Length; i++)
    {
        var c = char.ToLower(name[i]);
        if (c != ' ')
        {
            result[c] = (result.ContainsKey(c) ? result[c] : 0) + 1;
        }

    }
    return result;
}



//Replace digits with words in a string
//Write a method ReplaceDigits in the class Exercise that expects a string parameter called sentence and does the following:

//For every occurrence of the digits '0', '1', '2', '3', '4', '5', '6', '7', '8', and '9', replace them with the words 'zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', eight', or 'nine' respectively. Return the modified sentence with all digits replaced, and insert spaces where appropriate.

//So for the input string "4 score and 7 years ago, 8 men had the same PIN code: 6571", I expect the following output:

//"four score and seven years ago, eight men had the same PIN code: six five seven one"

//The exercise.cs file contains a number of bugs, and it is very inefficient in terms of memory use. Your task is to fix the bugs, and refactor the code to minimize the number of string objects created on the heap. 
string ReplaceDigits(string sentence)
{
    string[] words = { "zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine" };
    var resultBuilder = new StringBuilder();

    for (var i = 0; i < sentence.Length; i++)
    {
        var c = sentence[i];

        if ( c >= '0' && c <= '9')
        {
            resultBuilder.Append(words[c - '0']);
            if (i+1<sentence.Length && sentence[i + 1] != ' ')
                resultBuilder.Append(' ');
        }
        else
        {
            resultBuilder.Append(c);
        }

    }
    return resultBuilder.ToString();
}

string ReplaceDigitsSolution(string sentence)
{
    string[] words = { "zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine" };
    var result = new StringBuilder(1000);
    for (var index = 0; index < sentence.Length; index++)
    {
        var c = sentence[index];
        if (Char.IsDigit(c))
        {
            int digit = (int)Char.GetNumericValue(c);
            result.Append(words[digit]);
            if (index < sentence.Length - 1 && !Char.IsWhiteSpace(sentence[index + 1]))
                result.Append(' ');
        }
        else
            result.Append(c);
    }
    return result.ToString();
}

//Matrix multiplication
//Write a method Multiply in the class Exercise that expects two 2-dimensional matrices of type Matrix, and multiplies them.

//The example code works fine, but it is inefficient, your task is to speed up the code. Identify the performance bottleneck and refactor the code accordingly. 
Matrix Multiply(Matrix a, Matrix b)
{
    var result = new Matrix(new int[a.Rows, b.Columns]);
    for (int i = 0; i < result.Rows; i++)
    {
        for (int j = 0; j < result.Columns; j++)
        {
            result[i, j] = 0;
            for (int k = 0; k < a.Columns; k++)
                result[i, j] += (a[i, k] * b[k, j]);
        }
    }
    return result;
}
  

public class Matrix : IEnumerable
{
    private int[] _data;

    public int Rows { get; private set; }
    public int Columns { get; private set; }

    public int this[int row, int col]
    {
        get { return _data[row * Columns + col]; }
        set { _data[row  * Columns + col] = value; }
    }

    public Matrix(int[,] value)
    {
        Rows =   value.GetLength(0);
        Columns = value.GetLength(1);

        _data = new int[Rows * Columns];

        for (int i = 0; i < Rows; i++)
        {
            for (int j = 0; j < Columns; j++)
            {
                _data[i * Columns + j] = value[i, j];
            }
        }
    }

    IEnumerator IEnumerable.GetEnumerator()
    {
        return _data.GetEnumerator();
    }
}