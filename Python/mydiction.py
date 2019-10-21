# A dictionary is a collection which is unordered, changeable and indexed. In Python dictionaries are written with curly brackets, and they have keys and values.
thisdict = {
    "brand": "Ford",
    "model": "Mustang",
    "year": 1964
}
print(thisdict)

x = thisdict["model"]
x = "asd"
print(thisdict)
x = thisdict.get("model")
print(thisdict)
thisdict["year"] = 2018

for x in thisdict:
    print(x)
for x in thisdict.values():
    print(x)
for x, y in thisdict.items():
    print(x, y)

thisdict["color"] = "red"
print(thisdict)
thisdict.pop("model")
print(thisdict)

# The popitem() method removes the last inserted item (in versions before 3.7, a random item is removed instead):
thisdict.popitem()
print(thisdict)

del thisdict["year"]
print(thisdict)

mydict = thisdict.copy()
del thisdict
otherdict = dict(mydict)
print(mydict)

myfamily = {
    "child1": {
        "name": "Emil",
        "year": 2004
    },
    "child2": {
        "name": "Tobias",
        "year": 2007
    },
    "child3": {
        "name": "Linus",
        "year": 2011
    }
}
thisdict = dict(brand="Ford", model="Mustang", year=1964)
# note that keywords are not string literals
# note the use of equals rather than colon for the assignment
print(thisdict)
