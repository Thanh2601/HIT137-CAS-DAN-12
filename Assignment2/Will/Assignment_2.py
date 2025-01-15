import turtle

def draw_branch(t, branch_length, left_angle, right_angle, depth, reduction_factor):
    if depth == 0:
        return

    # Draw the main branch
    t.forward(branch_length)

    # Draw the left subtree
    t.left(left_angle)
    draw_branch(t, branch_length * reduction_factor, left_angle, right_angle, depth - 1, reduction_factor)
    t.right(left_angle)  # Return to the original angle

    # Draw the right subtree
    t.right(right_angle)
    draw_branch(t, branch_length * reduction_factor, left_angle, right_angle, depth - 1, reduction_factor)
    t.left(right_angle)  # Return to the original angle

    # Go back to the original position
    t.backward(branch_length)

def main():
    # Get user input
    left_angle = int(input("Enter the left branch angle (in degrees): "))
    right_angle = int(input("Enter the right branch angle (in degrees): "))
    branch_length = int(input("Enter the starting branch length (in pixels): "))
    depth = int(input("Enter the recursion depth: "))
    reduction_factor = float(input("Enter the branch length reduction factor (e.g., 0.7 for 70%): "))

    # Set up the turtle
    screen = turtle.Screen()
    screen.setup(width=800, height=600)
    screen.title("Recursive Tree Pattern")
    
    t = turtle.Turtle()
    t.speed("fastest")
    t.left(90)  # Point the turtle upwards
    t.penup()
    t.goto(0, -250)  # Move to the starting position
    t.pendown()

    # Draw the tree
    draw_branch(t, branch_length, left_angle, right_angle, depth, reduction_factor)

    # Keep the window open
    screen.mainloop()

if __name__ == "__main__":
    main()

