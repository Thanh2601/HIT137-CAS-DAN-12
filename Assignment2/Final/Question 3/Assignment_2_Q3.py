import turtle

def draw_tree(t, branch_len, left_angle, right_angle, reduction_factor, depth, width):
    if depth == 0 or branch_len < reduction_factor:
        return
    
    # Set color based on first branch (brown) or others (green)
    if depth == 5:  # First branch
        t.color("brown")
    else:
        t.color("green")
        width = width * 0.9  # Make green branches extra thin
    
    t.pensize(width)
    t.forward(branch_len)
    
    pos = t.pos()
    heading = t.heading()
    
    t.right(right_angle)
    draw_tree(t, branch_len * reduction_factor, left_angle, right_angle, 
             reduction_factor, depth - 1, width * 0.7)
    
    t.penup()
    t.setpos(pos)
    t.setheading(heading)
    t.pendown()
    
    t.left(left_angle)
    draw_tree(t, branch_len * reduction_factor, left_angle, right_angle, 
             reduction_factor, depth - 1, width * 0.7)
    
    t.penup()
    t.setpos(pos)
    t.setheading(heading)
    t.pendown()

#Enter the parameters
left_angle = float(input("Enter the left angle: "))
right_angle = float(input("Enter the right angle: "))
branch_len = float(input("Enter the initial branch length: "))
depth = int(input("Enter the depth of branching: "))
reduction = float(input("Enter the reduction factor for branch length: "))
initial_width = 10

# Set up the screen
screen = turtle.Screen()
screen.title("Assignment_2_Q3 Tree")
screen.bgcolor("white")

# Create and set up the turtle
t = turtle.Turtle()
t.speed(0)
t.left(90)
t.penup()
t.setpos(0, -200)
t.pendown()


draw_tree(t, branch_len, left_angle, right_angle, reduction, depth, initial_width)

t.hideturtle()
screen.mainloop()
