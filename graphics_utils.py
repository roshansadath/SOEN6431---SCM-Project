"""
# graphicsUtils.py
# ----------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
#
# Attribution Information:
# The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).

"""

import sys
import time
import tkinter
WINDOWS = sys.platform == 'win32'  # True if on Win95/98/NT

ROOTWINDOW = None      # The root window for graphics output
CANVAS = None      # The canvas which holds graphics
CANVAS_XS = None      # Size of canvas obj
CANVAS_YS = None
CANVAS_X = None      # Current position on canvas
CANVAS_Y = None
CANVAS_COL = None      # Current colour (set to black below)
CANVAS_TSIZE = 12
CANVAS_TSERIFS = 0


def format_color(red, green, blue):
    """Format the color into hexcode"""
    return ('#%02x%02x%02x' % (int(red * 255),
                               int(green * 255), int(blue * 255)))


def color_to_vector(color):
    """CHange color to vector"""
    return [int(_x, 16) / 256.0 for _x in [color[1:3], color[3:5], color[5:7]]]


if WINDOWS:
    CANVAS_tfonts = ['times new roman', 'lucida console']
else:
    CANVAS_tfonts = ['times', 'lucidasans-24']
    # need defaults here


def sleep(secs):
    """
    sleep function for given seconds
    """
    if ROOTWINDOW is None:
        time.sleep(secs)
    else:
        ROOTWINDOW.update_idletasks()
        ROOTWINDOW.after(int(1000 * secs), ROOTWINDOW.quit)
        ROOTWINDOW.mainloop()


def begin_graphics(width=640, height=480,
                   color=format_color(0, 0, 0), title=None):
    """start graphics"""
    global ROOTWINDOW, CANVAS, CANVAS_X
    global CANVAS_Y, CANVAS_XS, CANVAS_YS, _BG_COLOR

    # Check for duplicate call
    if ROOTWINDOW is not None:
        # Lose the window.
        ROOTWINDOW.destroy()

    # Save the canvas size parameters
    CANVAS_XS, CANVAS_YS = width - 1, height - 1
    CANVAS_X, CANVAS_Y = 0, CANVAS_YS
    _BG_COLOR = color

    # Create the root window
    ROOTWINDOW = tkinter.Tk()
    ROOTWINDOW.protocol('WM_DELETEwinDOW', _destroywindow)
    ROOTWINDOW.title(title or 'Graphics Window')
    ROOTWINDOW.resizable(0, 0)

    # Create the canvas obj
    try:
        CANVAS = tkinter.Canvas(ROOTWINDOW, width=width, height=height)
        CANVAS.pack()
        draw_background()
        CANVAS.update()
    except Exception:
        ROOTWINDOW = None
        raise

    # Bind to key-down and key-up events
    ROOTWINDOW.bind("<KeyPress>", _keypress)
    ROOTWINDOW.bind("<KeyRelease>", _keyrelease)
    ROOTWINDOW.bind("<FocusIn>", _clear_keys)
    ROOTWINDOW.bind("<FocusOut>", _clear_keys)
    ROOTWINDOW.bind("<Button-1>", _leftclick)
    ROOTWINDOW.bind("<Button-2>", _rightclick)
    ROOTWINDOW.bind("<Button-3>", _rightclick)
    ROOTWINDOW.bind("<Control-Button-1>", _ctrl_leftclick)
    _clear_keys()


_LEFT_CLICK_LOC = None
_RIGHT_CLICK_LOC = None
_CTRL_LEFT_CLICK_LOC = None


def _leftclick(event):
    global _LEFT_CLICK_LOC
    _LEFT_CLICK_LOC = (event._x, event._y)


def _rightclick(event):
    global _RIGHT_CLICK_LOC
    _RIGHT_CLICK_LOC = (event._x, event._y)


def _ctrl_leftclick(event):
    global _CTRL_LEFT_CLICK_LOC
    _CTRL_LEFT_CLICK_LOC = (event._x, event._y)


def wait_for_click():
    " Waiting for a click "
    while True:
        global _LEFT_CLICK_LOC
        global _RIGHT_CLICK_LOC
        global _CTRL_LEFT_CLICK_LOC
        if _LEFT_CLICK_LOC is not None:
            val = _LEFT_CLICK_LOC
            _LEFT_CLICK_LOC = None
            return val, 'left'
        if _RIGHT_CLICK_LOC is not None:
            val = _RIGHT_CLICK_LOC
            _RIGHT_CLICK_LOC = None
            return val, 'right'
        if _CTRL_LEFT_CLICK_LOC is not None:
            val = _CTRL_LEFT_CLICK_LOC
            _CTRL_LEFT_CLICK_LOC = None
            return val, 'ctrl_left'
        sleep(0.05)


def draw_background():
    " Draw background for the window "
    corners = [(0, 0), (0, CANVAS_YS),
               (CANVAS_XS, CANVAS_YS), (CANVAS_XS, 0)]
    polygon(corners, _BG_COLOR, fill_color=_BG_COLOR,
            filled=True, smoothed=False)


def _destroywindow():
    " Destroy Window "
    sys.exit(0)
#    global ROOTWINDOW
#    ROOTWINDOW.destroy()
#    ROOTWINDOW = None
    # print "DESTROY"


def end_graphics():
    " End the graphics "
    global ROOTWINDOW, CANVAS, _mouse_enabled
    try:
        try:
            sleep(1)
            if ROOTWINDOW is not None:
                ROOTWINDOW.destroy()
        except SystemExit as sysexit:
            print(('Ending graphics raised an exception:', sysexit))
    finally:
        ROOTWINDOW = None
        CANVAS = None
        _mouse_enabled = 0
        _clear_keys()


def clear_screen():
    " Clear the Screen "
    global CANVAS_X, CANVAS_Y
    CANVAS.delete('all')
    draw_background()
    CANVAS_X, CANVAS_Y = 0, CANVAS_YS


def polygon(coords, outline_color,
            fill_color=None, filled=1,
            smoothed=1, behind=0, width=1):
    """ Defining a Polygon """
    _c = []
    for coord in coords:
        c.append(coord[0])
        c.append(coord[1])
    if fill_color is None:
        fill_color = outline_color
    if filled == 0:
        fill_color = ""
    poly = CANVAS.create_polygon(
        c, outline=outline_color, fill=fill_color, smooth=smoothed, width=width)
    if behind > 0:
        CANVAS.tag_lower(poly, behind)  # Higher should be more visible
    return poly


def square(pos, _r, color, filled=1, behind=0):
    " Drawing a Square "
    _x, _y = pos
    coords = [(_x - _r, _y - _r), (_x + _r, _y - _r),
              (_x + _r, _y + _r), (_x - _r, _y + _r)]
    return polygon(coords, color, color, filled, 0, behind=behind)


def circle(pos, r,
           outline_color,
           fill_color,
           endpoints=None,
           style='pieslice',
           width=2):
    " Drawing a circle "
    _x, _y = pos
    _x0, _x1 = _x - _r - 1, _x + _r
    _y0, _y1 = _y - _r - 1, _y + _r
    if endpoints is None:
        _e = [0, 359]
    else:
        _e = list(endpoints)
    while _e[0] > _e[1]:
        _e[1] = _e[1] + 360

    return CANVAS.create_arc(x0, y0, x1, y1,
                              outline=outline_color,
                              fill=fill_color,
                              extent=e[1] - e[0],
                              start=e[0],
                              style=style,
                              width=width)


def image(pos, file="../../blueghost.gif"):
    " Get Image "
    _x, _y = pos
    # img = PhotoImage(file=file)
    return CANVAS.create_image(_x,
                               _y,
                               image=tkinter.PhotoImage(file=file),
                               anchor=tkinter.NW)


def refresh():
    " Refresh Canvas "
    CANVAS.update_idletasks()


def move_circle(id, pos, r, endpoints=None):
    global CANVAS_X, CANVAS_Y

    _x, _y = pos
#    _x0, _x1 = _x - r, _x + r + 1
#    _y0, _y1 = _y - r, _y + r + 1
    _x0, _ = _x - _r - 1, _x + _r
    _y0, _ = _y - _r - 1, _y + _r
    if endpoints is None:
        _e = [0, 359]
    else:
        _e = list(endpoints)
    while _e[0] > _e[1]:
        _e[1] = _e[1] + 360

    edit(_id, ('start', _e[0]), ('extent', _e[1] - _e[0]))
    move_to(_id, _x0, _y0)


def edit(_id, *args):
    " Edit Canvas "
    CANVAS.itemconfigure(_id, **dict(args))


def text(pos,
         color,
         contents,
         font='Helvetica',
         size=12,
         style='normal',
         anchor="nw"):
    " Add Text "
    global CANVAS_X, CANVAS_Y
    _x, _y = pos
    font = (font, str(size), style)
    return CANVAS.create_text(_x,
                              _y,
                              fill=color,
                              text=contents,
                              font=font,
                              anchor=anchor)


def change_text(id, newText, font=None, size=12, style='normal'):
    CANVAS.itemconfigure(id, text=newText)
    if font is not None:
        CANVAS.itemconfigure(_id, font=(font, '-%d' % size, style))


def change_color(_id, new_color):
    " Change Color "
    CANVAS.itemconfigure(_id, fill=new_color)


def line(here, there, color=format_color(0, 0, 0), width=2):
    " Define a Line "
    _x0, _y0 = here[0], here[1]
    _x1, _y1 = there[0], there[1]
    return CANVAS.create_line(_x0, _y0, _x1, _y1, fill=color, width=width)


"""
#############################
### Keypress handling #######
#############################

"""

# We bind to key-down and key-up events.

_keysdown = {}
_keyswaiting = {}
# This holds an unprocessed key release.  We delay key releases by up to
# one call to keys_pressed() to get round a problem with auto repeat.
_got_release = None


def _keypress(event):
    global _got_release
    # remap_arrows(event)
    _keysdown[event.keysym] = 1
    _keyswaiting[event.keysym] = 1
#    print event.char, event.keycode
    _got_release = None


def _keyrelease(event):
    global _got_release
    # remap_arrows(event)
    try:
        del _keysdown[event.keysym]
    except UserWarning:
        pass
    _got_release = 1


def _clear_keys():
    " Clear Keys "
    global _keysdown, _got_release, _keyswaiting
    _keysdown = {}
    _keyswaiting = {}
    _got_release = None


def keys_pressed(d_o_e=None,
                 d_w=tkinter._tkinter.DONT_WAIT):
    " Check Keys Pressed "
    if d_o_e is None:
        d_o_e = ROOTWINDOW.dooneevent
    d_o_e(d_w)
    if _got_release:
        d_o_e(d_w)
    return list(_keysdown.keys())


def keys_waiting():
    " Waiting foe keys "
    global _keyswaiting
    keys = list(_keyswaiting.keys())
    _keyswaiting = {}
    return keys

# Block for a list of keys...


def wait_for_keys():
    " Wait for Keys "
    keys = []
    while not keys:
        keys = keys_pressed()
        sleep(0.05)
    return keys


def remove_from_screen(_x,
                       d_o_e=None,
                       d_w=tkinter._tkinter.DONT_WAIT):
    " Remove Window from Screen "
    if d_o_e is None:
        d_o_e = ROOTWINDOW.dooneevent
    CANVAS.delete(_x)
    d_o_e(d_w)


def _adjust_coords(coord_list, _x, _y):
    "Adjusting Coordinates"
    for i in range(0, len(coord_list), 2):
        coord_list[i] = coord_list[i] + _x
        coord_list[i + 1] = coord_list[i + 1] + _y
    return coord_list


def move_to(obj, _x, _y=None,
            d_o_e=None,
            d_w=tkinter._tkinter.DONT_WAIT):
    " A Move To Function "
    if d_o_e is None:
        d_o_e = ROOTWINDOW.dooneevent
    if _y is None:
        try:
            _x, _y = _x
        except Exception as exception:
            raise exception

    horiz = True
    new_coords = []
    current_x, current_y = CANVAS.coords(obj)[0:2]  # first point
    for coord in CANVAS.coords(obj):
        if horiz:
            inc = _x - current_x
        else:
            inc = _y - current_y
        horiz = not horiz

        new_coords.append(coord + inc)

    CANVAS.coords(obj, *new_coords)
    d_o_e(d_w)


def move_by(obj, x_pos, y_pos=None,
            d_o_e=None,
            d_w=tkinter._tkinter.DONT_WAIT, lift=False):
    """Move the pac based on the position"""
    if d_o_e is None:
        d_o_e = ROOTWINDOW.dooneevent
    if y_pos is None:
        try:
            x_pos, y_pos = x_pos
        except Exception as exc:
            raise exc

    horiz = True
    new_coords = []
    for coord in CANVAS.coords(obj):
        if horiz:
            inc = x_pos
        else:
            inc = y_pos
        horiz = not horiz

        new_coords.append(coord + inc)

    CANVAS.coords(obj, *new_coords)
    d_o_e(d_w)
    if lift:
        CANVAS.tag_raise(obj)


def write_post_script(filename):
    "Writes the current canvas to a postscript file."
    with open(filename, 'w', encoding="utf8") as psfile:
        psfile.write(CANVAS.postscript(pageanchor='sw', _y='0._c', _x='0._c'))


ghost_shape = [
    (0, - 0.5),
    (0.25, - 0.75),
    (0.5, - 0.5),
    (0.75, - 0.75),
    (0.75, 0.5),
    (0.5, 0.75),
    (- 0.5, 0.75),
    (- 0.75, 0.5),
    (- 0.75, - 0.75),
    (- 0.5, - 0.5),
    (- 0.25, - 0.75)
]

if __name__ == '__main__':
    begin_graphics()
    clear_screen()
    ghost_shape = [(_x * 10 + 20, _y * 10 + 20) for _x, _y in ghost_shape]
    g = polygon(ghost_shape, format_color(1, 1, 1))
    move_to(g, (50, 50))
    circle((150, 150), 20, format_color(0.7, 0.3, 0.0),
           fill_color=None, endpoints=[15, - 15])
    sleep(2)
