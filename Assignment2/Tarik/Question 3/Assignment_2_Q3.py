import turtle

def draw_tree(t, branch_len, left_angle, right_angle, reduction_factor, depth, width):
    if depth == 0 or branch_len < 5:
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

left_angle = 20    # 20 degrees left
right_angle = 25   # 25 degrees right
branch_len = 100   # 100 pixels initial length
depth = 5         # branch out 5 times
reduction = 0.7    # 70% of parent branch
initial_width = 10  # Reduced from 15 to 10 for thinner overall branches

draw_tree(t, branch_len, left_angle, right_angle, reduction, depth, initial_width)

t.hideturtle()
screen.mainloop()