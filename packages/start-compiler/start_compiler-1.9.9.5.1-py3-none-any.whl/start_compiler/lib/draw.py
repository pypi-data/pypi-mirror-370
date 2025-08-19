import turtle

pen = False
color = [0, 0, 0]
sprites = {}
screen = None

def setup():
    global pen
    global turtle_init
    global screen

    if not pen:
        # Create a turtle object
        pen = turtle.Turtle()
        # Set up the canvas
        turtle.tracer(0)
        screen = turtle.Screen()
        screen.title("Start draw")
        screen.bgcolor("white")
        screen.colormode(255)  # Enable RGB color mode (0-255)
        screen.setworldcoordinates(-50, -50, 50, 50)

def _color(r, g, b):
    global pen, color
    setup()
    pen.pencolor(r.value, g.value, b.value)
    color[0] = r.value
    color[1] = g.value
    color[2] = b.value

def _line(x, y, x2, y2):
    global pen
    setup()
    pen.penup()
    pen.goto(x.value, y.value)
    pen.pendown()
    pen.goto(x2.value, y2.value)
    turtle.update()

def _circle(x, y, r):
    global pen
    setup()
    pen.penup()
    pen.goto(x.value, y.value)
    pen.pendown()
    pen.circle(r.value)
    turtle.update()

def _axes():
    global pen, color
    setup()
    pen.pencolor(128, 128, 128)
    pen.penup()
    pen.goto(-50, 0)
    pen.pendown()
    pen.goto(50, 0)
    pen.penup()
    pen.goto(0, -50)
    pen.pendown()
    pen.goto(0, 50)
    pen.penup()

    for i in range(-50, 51, 10):
        pen.goto(i, 1)
        pen.pendown()
        pen.write(i)
        pen.penup()
        pen.goto(1, i)
        pen.pendown()
        pen.write(i)
        pen.penup()
    pen.pencolor(color[0], color[1], color[2])

def _sprite(id, x, y, gif):
    global screen
    setup()
    if id.value not in sprites:
        sprite = turtle.Turtle()
        screen.register_shape(gif.value)
        sprite.shape(gif.value)  # Use the custom shape
        sprite.penup()
        sprites[id.value] = sprite
    else:
        sprite = sprites[id.value]
    sprite.goto(x.value, y.value)
    turtle.update()
