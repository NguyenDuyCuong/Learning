# A RegEx, or Regular Expression, is a sequence of characters that forms a search pattern.
# RegEx can be used to check if a string contains the specified search pattern.
import re

txt = "The rain in Spain"
x = re.search("^The.*Spain$", txt)
print(x.start())

str = "The rain in Spain"
x = re.split("\s", str)
print(x)

# Replace every white-space character with the number 9:
str = "The rain in Spain"
x = re.sub("\s", "9", str)
print(x)

# Replace the first 2 occurrences:
str = "The rain in Spain"
x = re.sub("\s", "9", str, 2)
print(x)