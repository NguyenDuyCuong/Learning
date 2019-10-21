# A set is a collection which is unordered and unindexed. In Python sets are written with curly brackets.
# You cannot access items in a set by referring to an index, since sets are unordered the items has no index.
thisset = {"apple", "banana", "cherry"}
print(thisset)
for x in thisset:
    print(x)

thisset.add("orange")
print(thisset)

thisset.update(["orange", "mango", "grapes"])
print(thisset)

# To remove an item in a set, use the remove(), or the discard() method.
thisset.discard("as")
# If the item to remove does not exist, remove() will raise an error.
# thisset.remove("as")
print(thisset)

# Remove the last item by using the pop() method:
# Sets are unordered, so when using the pop() method, you will not know which item that gets removed.
x = thisset.pop()
print(x)
print(thisset)

# You can use the union() method that returns a new set containing all items from both sets, or the update() method that inserts all the items from one set into another:
# Both union() and update() will exclude any duplicate items.
set1 = {"a", "b", "c"}
set2 = {1, 2, 3}

set3 = set1.union(set2)
print(set3)
set1.update(set2)
print(set1)

# The set() Constructor
thisset = set(("apple", "banana", "cherry"))  # note the double round-brackets
print(thisset)
