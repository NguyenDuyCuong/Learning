a = '''Lorem ipsum dolor sit amet,
consectetur adipiscing elit,
sed do eiusmod tempor incididunt
ut labore et dolore magna aliqua.'''
print(a)

a = "Hello, World!"
print(a[1])

# Slicing
print(a[2:5])

# Negative Indexing
print(a[-5:-2])

txt = "The rain in Spain stays mainly in the plain"
x = "ain" in txt
print(x)

a = "Hello"
b = "World"
c = a + " " + b
print(c)


quantity = 3
itemno = 567
price = 49.95
myorder = "I want to pay {2} dollars for {0} pieces of item {1}."
print(myorder.format(quantity, itemno, price))
