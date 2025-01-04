import turtle

# Recursive function to draw the tree
def draw_tree(t, branch_length, angle_left, angle_right, depth, reduction_factor):
    if depth == 0:
        return
    if depth == recursion_depth:
        t.color("brown")  # Main trunk is brown
    else:
        t.color("green")  # All other branches are green
    # Draw the current branch
    t.forward(branch_length)

    # Draw the left branch
    t.left(angle_left)
    draw_tree(t, branch_length * reduction_factor, angle_left, angle_right, depth - 1, reduction_factor)
    
    # Return to the current branch
    t.right(angle_left + angle_right)
    
    # Draw the right branch
    draw_tree(t, branch_length * reduction_factor, angle_left, angle_right, depth - 1, reduction_factor)
    
    # Return to the trunk
    t.left(angle_right)
    t.backward(branch_length)

# Function to set up the turtle
def setup_turtle():
    screen = turtle.Screen()
    screen.bgcolor("white")
    t = turtle.Turtle()
    t.left(90)  # Start by drawing upwards
    t.speed(0)  # Set turtle to maximum speed
    return t

def main():
    # Get parameters from user input
    global recursion_depth
    angle_left = float(input("Enter the left branch angle (degrees): "))
    angle_right = float(input("Enter the right branch angle (degrees): "))
    starting_branch_length = float(input("Enter the starting branch length (pixels): "))
    recursion_depth = int(input("Enter the recursion depth: "))
    reduction_factor = float(input("Enter the branch length reduction factor (between 0 and 1): "))

    # Setup the turtle
    t = setup_turtle()

    # Position the turtle at the starting point
    t.penup()
    t.goto(0, -200)  # Start at the bottom of the screen
    t.pendown()
 
    # Start drawing the tree
    draw_tree(t, starting_branch_length, angle_left, angle_right, recursion_depth, reduction_factor)

    # Finish the drawing
    turtle.done()

# Call the main function to run the program
if __name__ == "__main__":
    main()
