import pytest
from turtleshell import Screen, Turtle

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

@pytest.fixture
def pen():
  Screen().tracer(0)
  _pen = Turtle(visible=False)
  return _pen

@pytest.fixture
def screen():
  return Screen()

def test_x(pen):
  pen.setx(100)
  assert pen.x == 100

def test_y(pen):
  pen.sety(200)
  assert pen.y == 200

def test_shapesize_set(pen):
  pen.shape("square")
  pen.shapesize(30,40)
  width, height, outline = pen.shapesize()
  assert width == 30
  assert height == 40
  assert outline == 1

def test_shapesize_get(pen):
  pen.shape("square")
  pen.shapesize(30, 40, 2)
  width, height, outline = pen.shapesize()
  assert width == 30
  assert height == 40
  assert outline == 2

def test_teleport(pen):
  assert pen.position() == (0, 0)
  pen.pendown()
  pen.teleport(100, 200)
  assert pen.position() == (100, 200) 
  assert len(pen.currentLine) == 1 # single point => no line drawn
  assert pen.isdown() # pen still down

def test_hsv_hue(pen):
  # pencolor
  pen.penhue(0)
  assert pen.pencolor() == RED
  pen.penhue(120)
  assert pen.pencolor() == GREEN
  pen.penhue(240)
  assert pen.pencolor() == BLUE

  # fillcolor
  pen.fillhue(0)
  assert pen.fillcolor() == RED
  pen.fillhue(120)
  assert pen.fillcolor() == GREEN
  pen.fillhue(240)
  assert pen.fillcolor() == BLUE
  
def test_hsv_saturation(pen):
  # pencolor
  pen.pensat(0)
  assert pen.pencolor() == WHITE
  pen.pensat(50)
  assert pen.pencolor() == (255, 128, 128) # light red
  pen.pensat(100)
  assert pen.pencolor() == RED
  
  # fillcolor
  pen.fillsat(0)
  assert pen.fillcolor() == WHITE
  pen.fillsat(50)
  assert pen.fillcolor() == (255, 128, 128) # light red
  pen.fillsat(100)
  assert pen.fillcolor() == RED
  
def test_hsv_value(pen):
  # pencolor
  pen.penval(0)
  assert pen.pencolor() == BLACK
  pen.penval(50)
  assert pen.pencolor() == (128, 0, 0) # dark red
  pen.penval(100)
  assert pen.pencolor() == RED
  
  # fillcolor
  pen.fillval(0)
  assert pen.fillcolor() == BLACK
  pen.fillval(50)
  assert pen.fillcolor() == (128, 0, 0) # dark red
  pen.fillval(100)
  assert pen.fillcolor() == RED
    
def test_color(pen, screen):
  # Colors are clamped to [0, 255]
  pen.pencolor(-20, -5, 0)
  assert pen.pencolor() == BLACK

  pen.pencolor(300, 300, 300)
  assert pen.pencolor() == WHITE

  # Floats are rounded
  screen.bgcolor(255, 0.3, 0)
  assert screen.bgcolor() == (255, 0, 0)

  screen.bgcolor(255, 0.7, 0)
  assert screen.bgcolor() == (255, 1, 0)