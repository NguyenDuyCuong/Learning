i = 1
while i < 6:
    print(i)
    if i == 3:
        break
    i += 1
else:
    print("i is no longer less than 6")

fruits = ["apple", "banana", "cherry"]
for x in fruits:
    print(x)

for x in "banana":
    print(x)

for x in range(6):
    print(x)

# The range() function defaults to increment the sequence by 1, however it is possible to specify the increment value by adding a third parameter: range(2, 30, 3):
for x in range(2, 30, 3):
    print(x)

for x in range(6):
    print(x)
else:
    print("Finally finished!")

for x in [0, 1, 2]:
    pass
