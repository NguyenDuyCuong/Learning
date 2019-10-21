# & 	AND	Sets each bit to 1 if both bits are 1
# |	OR	Sets each bit to 1 if one of two bits is 1
# ^	XOR	Sets each bit to 1 if only one of two bits is 1
# ~ 	NOT	Inverts all the bits
# << Zero fill left shift Shift left by pushing zeros in from the right and let the leftmost bits fall off
# >> Signed right shift Shift right by pushing copies of the leftmost bit in from the left, and let the rightmost bits fall off

print('{0:08b}'.format(5))
print('{0:08b}'.format(3))
print('{0:08b}'.format(6))
print('{0:08b}'.format(3 << 1))
print(5 & 3)
print(5 | 3)
