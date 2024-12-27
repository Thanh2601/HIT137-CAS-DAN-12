#%%
a = int(input("Enter the first number: "))
b = int(input("Enter the second number: "))
c = int(input("Enter the third number: "))

# Check if the numbers can form a triangle
if (a + b > c) and (a + c > b) and (b + c > a):
    print("Yes, these three lengths can form a triangle.")
else:
    print("NO, these three lengths CANNOT form a triangle.")

#%%
size = int(input("Enter the size of the square: "))

# Draw the square
for i in range(size):
    if (i == 0 or i == size - 1):
        print("* " * size)
    else:
        print("* " + "  " * (size - 2) + "*")

# %%
