def can_form_triangle():
    # Input three numbers
    a = float(input("Enter the first number: "))
    b = float(input("Enter the second number: "))
    c = float(input("Enter the third number: "))
    
    # Check the triangle inequality
    if a + b > c and a + c > b and b + c > a:
        print("Yes, these three lengths can form a triangle.")
    else:
        print("NO, these three lengths CANNOT form a triangle.")

# Run the function
can_form_triangle()
