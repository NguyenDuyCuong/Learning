print(10 > 9)
print(10 == 9)
print(10 < 9)

print(bool("Hello"))
print(bool(15))
print(bool(""))

# Any string is True, except empty strings.
# Any number is True, except 0.
# Any list, tuple, set, and dic tionary are True, except empty ones.
bool(False)
bool(None)
bool(0)
bool("")
bool(())
bool([])
bool({})

'''One more value, or object in this case, evaluates to False, and that is if you have an objects that are made from a class with a __len__ function that returns 0 or False:'''


class myclass():
    def __len__(self):
        return 0


myobj = myclass()
print(bool(myobj))

# Functions can Return a Boolean
x = 200
print(isinstance(x, int))
