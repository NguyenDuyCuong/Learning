# Consider a module to be the same as a code library.
# A file containing a set of functions you want to include in your application.
import mylambda as L
from mylambda import mydoubler

print(L.mytripler(11))
print(mydoubler(11))

# Built-in Modules
import platform

x = platform.system()
print(x)
x = dir(platform)
print(x)