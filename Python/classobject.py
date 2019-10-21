# Python is an object oriented programming language.
# Almost everything in Python is an object, with its properties and methods.
# A Class is like an object constructor, or a "blueprint" for creating objects.

class MyClass:
  x = 5

p1 = MyClass()
print(p1.x)

# The __init__() Function
# All classes have a function called __init__(), which is always executed when the class is being initiated.
class Person:
  def __init__(self, name, age):
    self.name = name
    self.age = age

  def myfunc(self):
    print("Hello my name is " + self.name)

p1 = Person("John", 36)
p1.myfunc()

# The self parameter is a reference to the current instance of the class, and is used to access variables that belong to the class.
# It does not have to be named self , you can call it whatever you like, but it has to be the first parameter of any function in the class:
class Person:
  def __init__(mysillyobject, name, age):
    mysillyobject.name = name
    mysillyobject.age = age

  def myfunc(abc):
    print("Hello my name is " + abc.name)

p1 = Person("John", 36)
p1.myfunc()


# Delete Object Properties
del p1.age
# Delete Objects
del p1

# class definitions cannot be empty, but if you for some reason have a class definition with no content, put in the pass statement to avoid getting an error.
class Person:
  pass
