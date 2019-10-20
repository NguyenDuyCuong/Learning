x = 12
x = "Ab"
X = 1
print(x)
print(X)

x, y, z = "Orange", "Banana", "Cherry"
print(x)
print(y)
print(z)

x = y = z = "Orange"
print(x)
print(y)
print(z)


x = "awesome"


def myfunc():
    x = "fantastic"
    global y
    y = "YY"
    print("Python is " + x)


myfunc()
print("Python is " + x)
print("Y = " + y)
