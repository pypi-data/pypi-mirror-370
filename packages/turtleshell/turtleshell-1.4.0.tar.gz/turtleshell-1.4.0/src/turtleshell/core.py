"""Convenience wrappers around turtle.Turtle and turtle.Screen
  See https://github.com/python/cpython/blob/main/Lib/turtle.py
  """
#TODO handle floats, randcoords, default screensize, default shape
#TODO # def _polytrafo(self, poly):
import colorsys, math, turtle
from dataclasses import dataclass

sign = lambda x: round(math.copysign(1, x))

@dataclass
class HSV:
  hue: float
  sat: float
  val: float
  def __iter__(self):
    return iter(self.__dict__.values())

def Screen():
    """Return the singleton screen object."""
    if Turtle._screen is None:
        Turtle._screen = _Screen()
    return Turtle._screen

class _Screen(turtle._Screen):
  def __init__(self):
    super().__init__()
    turtle.TurtleScreen.__init__(self, _Screen._canvas)
    if turtle.Turtle._screen is None:
      turtle.Turtle._screen = self
    self.colormode(255)
    self.timers = {}

  def register_shape(self, name, shape=None):
      """Adds a turtle shape to TurtleScreen's shapelist.

      Arguments:
      (1) name is the name of a gif- or png- file and shape is None.
          Installs the corresponding image shape.
          !! Image-shapes DO NOT rotate when turning the turtle,
          !! so they do not display the heading of the turtle!
      (2) name is an arbitrary string and shape is a tuple
          of pairs of coordinates. Installs the corresponding
          polygon shape
      (3) name is an arbitrary string and shape is a
          (compound) Shape object. Installs the corresponding
          compound shape.
      To use a shape, you have to issue the command shape(shapename).

      call: register_shape("turtle.gif")
      --or: register_shape("tri", ((0,0), (10,10), (-10,10)))

      Example (for a TurtleScreen instance named screen):
      >>> screen.register_shape("triangle", ((5,-3),(0,5),(-5,-3)))

      """
      if shape is None:
          # image
          if (name.lower().endswith(".gif") or 
              name.lower().endswith(".png")):
              shape = turtle.Shape("image", self._image(name))
          else:
              raise turtle.TurtleGraphicsError("Bad arguments for register_shape.\n"
                                        + "Use  help(register_shape)" )
      elif isinstance(shape, tuple):
          shape = turtle.Shape("polygon", shape)
      ## else shape assumed to be Shape-instance
      self._shapes[name] = shape

  def _drawimage(self, item, pos, image):
      """Configure image item as to draw image object
      at position (x,y) on canvas)
      """
      x, y = pos
      self.cv.coords(item, (x * self.xscale, -y * self.yscale))
      self.cv.itemconfig(item, image=image)
       # bring image-based sprites to front, just as shape-based sprites are
      self.cv.tag_raise(item)

  @property
  def width(self):
    return self.window_width()
  
  @property
  def height(self):
    return self.window_height()
  
  def setup(self, width=turtle._CFG["width"], height=turtle._CFG["height"],
            startx=turtle._CFG["leftright"], starty=turtle._CFG["topbottom"]):
    super().setup(width, height, startx, starty)
    self.screensize(self.width-20, self.height-20)

  def _onkeypress(self, fun, key=None):
    if fun is None:
      if key is None:
        for key in self._keys:
          self._keys.remove(key)
          self.cv.unbind("<KeyPress-%s>" % key, None)
      else:
        self.cv.unbind("<KeyPress-%s>" % key, None)
    else:
      def eventfun(event):
        fun()
      if key is None:
        self.cv.bind("<KeyPress>", eventfun)
      else:
        self.cv.bind("<KeyPress-%s>" % key, eventfun)

  def onmove(self, fun):
    def eventfun(event):
      x, y = (self.cv.canvasx(event.x)/self.xscale,
              -self.cv.canvasy(event.y)/self.yscale)
      fun(x, y)
    self.cv.bind("<Motion>", eventfun)

  def cancel_timer(self, func):
    if not func in self.timers:
      return
    for id in self.timers.pop(func):
      self.getcanvas().after_cancel(id)

  def set_timer(self, func, ms, add=False):
    if not add and func in self.timers:
      self.cancel_timer(func)
    id = self.getcanvas().after(ms, func)
    if func in self.timers:
      self.timers[func].append(id)
    else:
      self.timers[func] = [id]

  def _colorstr(self, color):
    isnumber = lambda x: isinstance(x, (int, float))
    if isinstance(color, tuple) and len(color) == 1:
      color = color[0]
    if len(color) == 3 and all([isnumber(c) for c in color]):
      lower, upper = 0, Turtle._screen.colormode()
      color = [max(min(upper, round(c)), lower) for c in color]
    return super()._colorstr(color)

def _hsv_to_rgb(hsv):
  rgb = colorsys.hsv_to_rgb(*hsv)
  return [round(c*Turtle._screen.colormode()) for c in rgb]

class Turtle(turtle.RawTurtle):

  _pen = None
  _screen = None
  MULT = 20

  def __init__(self,
              shape=turtle._CFG["shape"],
              undobuffersize=turtle._CFG["undobuffersize"],
              visible=turtle._CFG["visible"]):
    if Turtle._screen is None:
      Turtle._screen = Screen()
    turtle.RawTurtle.__init__(self, Turtle._screen,
                        shape=shape,
                        undobuffersize=undobuffersize,
                        visible=visible)
    self.shapesize(Turtle.MULT)
    self._pen_hsv = HSV(0, 1, 1)
    self._fill_hsv = HSV(0, 1, 1)

  def __lt__(self, other):
    if isinstance(other, Turtle):
      return self.y < other.y
    return NotImplemented
  
  def __eq__(self, other):
    if isinstance(other, Turtle):
      return self.y == other.y
    return NotImplemented

  def onenter(self, fun):
    titem = self.turtle._item
    if fun is None:
      self.screen.cv.tag_unbind(titem, "<Enter>")
    else:
      def eventfun(event):
        x, y = (self.screen.cv.canvasx(event.x)/self.screen.xscale,
                -self.screen.cv.canvasy(event.y)/self.screen.yscale)
        fun(x, y)
      self.screen.cv.tag_bind(titem, "<Enter>", eventfun)

  def onexit(self, fun):
    titem = self.turtle._item
    if fun is None:
      self.screen.cv.tag_unbind(titem, "<Leave>")
    else:
      def eventfun(event):
        x, y = (self.screen.cv.canvasx(event.x)/self.screen.xscale,
                -self.screen.cv.canvasy(event.y)/self.screen.yscale)
        fun(x, y)
      self.screen.cv.tag_bind(titem, "<Leave>", eventfun)

  def bring_forward(self):
      titem = self.turtle._item
      for item in self.items:
        self.screen.cv.tag_raise(item)
      titem = self.turtle._item
      self.screen.cv.tag_raise(titem)

  def send_backward(self):
      titem = self.turtle._item
      self.screen.cv.tag_lower(titem)

  def face(self, x, y):
    self.setheading(self.towards(x, y))

  @property
  def x(self):
    return self.xcor()

  @x.setter
  def x(self, value):
    self.setx(value)

  @property
  def y(self):
    return self.ycor()

  @y.setter
  def y(self, value):
    self.sety(value)

  def shapesize(self, stretch_wid=None, stretch_len=None, outline=None):

    if stretch_wid is None and stretch_len is None and outline is None:
      stretch_wid, stretch_len, outline = super().shapesize()
      return stretch_wid*Turtle.MULT, stretch_len*Turtle.MULT, outline

    stretch_wid = stretch_wid/Turtle.MULT if stretch_wid else None
    stretch_len = stretch_len/Turtle.MULT if stretch_len else None
    ret = super().shapesize(stretch_wid, stretch_len, outline)
    return ret

  def teleport(self, x, y):
    pendown = self.isdown()
    if pendown:
      self.pen(pendown=False)
    self.penup()
    self._position = turtle.Vec2D(x, y)
    self.pen(pendown=pendown)
  
  def _write(self, txt, align, font):
        """Performs the writing for write()
        """
        item, end = self.screen._write(self._position, txt, align, font,
                                                          self._pencolor)
        
        self._update()
        self.items.append(item)
        if self.undobuffer:
            self.undobuffer.push(("wri", item))
        return end
  
  def write(self, arg, move=False, align="center", font=None, fontsize=None):
    if font is not None and fontsize is not None:
      raise ValueError("Can only specify one of font or fontsize")
    if fontsize is not None:
      font = ("Courier New", fontsize, "bold")
    elif font is None:
      font = ("Courier New", 20, "bold")
    super().write(arg, move, align, font)
    self.bring_forward() # TODO this will be undone if Screen.update() is called

  def to_front(self):
    self.goto(self.position())

  ## HSV colour methods
  def hsv(self, hue, sat, val):
    return

  def penhsv(self, *args):
    print(args)

  def fillhsv(self, *args):
    print(args)
    
  def hue(self, degrees=None):
    return (self.penhue(degrees), self.fillhue(degrees))

  def penhue(self, degrees=None):
    if degrees is None:
      return self._pen_hsv.hue * 360
    self._pen_hsv.hue = degrees/360
    self.pencolor(_hsv_to_rgb(self._pen_hsv))
    return degrees

  def fillhue(self, degrees=None):
    if degrees is None:
      return self._fill_hsv.hue * 360
    self._fill_hsv.hue = degrees/360
    self.fillcolor(_hsv_to_rgb(self._fill_hsv))

  def sat(self, value=None):
    return(self.pensat(value), self.fillsat(value))

  def pensat(self, value=None):
    if value is None:
      return self._pen_hsv.sat * 100
    self._pen_hsv.sat = value/100
    self.pencolor(_hsv_to_rgb(self._pen_hsv))

  def fillsat(self, value=None):
    if value is None:
      return self._fill_hsv.sat * 100
    self._fill_hsv.sat = value/100
    self.fillcolor(_hsv_to_rgb(self._fill_hsv))

  def val(self, value=None):
    return (self.penval(value), self.fillval(value))

  def penval(self, value=None):
    if value is None:
      return self._pen_hsv.val * 100
    self._pen_hsv.val = value/100
    self.pencolor(_hsv_to_rgb(self._pen_hsv))

  def fillval(self, value=None):
    if value is None:
      return self._fill_hsv.val * 100
    self._fill_hsv.val = value/100
    self.fillcolor(_hsv_to_rgb(self._fill_hsv))

Pen = Turtle

def turtle_test(screen):
  pen = Turtle()
  print(f"\n\n***\nTURTLE TYPE: {type(pen)}\nSCREEN TYPE: {type(screen)}\n***\n")
  pen.shape("square")
  pen.shapesize(30, 25)
  pen.hsv(100, 50, 50)
  pen.stamp()

if __name__ == "__main__":
  import os;os.system("clear")
  screen = Screen()
  screen.setup(400,400,0,0)
  screen.bgcolor("gold")
  turtle_test(screen)
  screen.exitonclick()
