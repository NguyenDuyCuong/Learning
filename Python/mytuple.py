# A tuple is a collection which is ordered and unchangeable. In Python tuples are written with round brackets.
thistuple = ("apple", "banana", "cherry", "orange", "kiwi", "melon", "mango")
# the items from index -4 (included) to index -1 (excluded)
print(thistuple[-4:-1])

thistuple = ("apple",)
print(type(thistuple))

# NOT a tuple
thistuple = ("apple")
print(type(thistuple))

# The del keyword can delete the tuple completely:
del thistuple

tuple1 = ("a", "b", "c")
tuple2 = (1, 2, 3)

tuple3 = tuple1 + tuple2
print(tuple3)

# note the double round-brackets
thistuple = tuple(("apple", "banana", "cherry"))
print(thistuple)
