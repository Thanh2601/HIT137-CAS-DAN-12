#1.a
sides = []

for i in range(3):
    sides.append(int(input(f"User input {i+1}: ")))

if ((sides[0] + sides[1]) < sides[2]) and ((sides[1] + sides[2]) < sides[0]) and ((sides[0] + sides[2]) < sides[1]):
    print(f"NO, these three lengths CANNOT form a triangle.")
else:
    print(f"Yes, these three lengths can form a triangle.")

# %%
#1.b
size = int(input(f"User input size: "))

for i in range(size):
    for j in range(size):
        if (i == 0): 
            print("* ",end='')
            if (j == (size-1)):
                print("")
        elif (i == (size-1)):
            print("* ",end='')
        else:
            if (j == 0):
                print("* ",end='')
            elif (j == (size-1)):
                print("* ")
            else:
                print("  ",end='')

# %%

