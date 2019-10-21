a = 200
b = 33
if b > a:
    print("b is greater than a")
elif a == b:
    print("a and b are equal")
else:
    print("a is greater than b")

if a > b:
    print("a is greater than b")

a = 330
b = 330
print("A") if a > b else print("=") if a == b else print("B")

# if statements cannot be empty, but if you for some reason have an if statement with no content, put in the pass statement to avoid getting an error.
if b > a:
    pass
