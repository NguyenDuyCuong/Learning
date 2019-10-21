# List is a collection which is ordered and changeable. Allows duplicate members.
# Tuple is a collection which is ordered and unchangeable. Allows duplicate members.
# Set is a collection which is unordered and unindexed. No duplicate members.
# Dictionary is a collection which is unordered, changeable and indexed. No duplicate members.

thislist = ["apple", "banana", "cherry", "orange", "kiwi", "melon", "mango"]
print(thislist[-4:-1])
if "apple" in thislist:
    print("Yes, 'apple' is in the fruits list")

# The del keyword removes the specified index:
del thislist[0]
print(thislist)

mylist = thislist.copy()
del thislist
otherlist = list(mylist)
print(mylist)
print(otherlist)

list1 = ["a", "b", "c"]
list2 = [1, 2, 3]
list3 = list1 + list2
print(list3)
list1.extend(list2)
print(list1)

# It is also possible to use the list() constructor to make a new list.
# note the double round-brackets
thislist = list(("apple", "banana", "cherry"))
print(thislist)
