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

ROOT_WINDOW = None      # The root window for graphics output
CANVAS = None      # The canvas which holds graphics
CANVAS_XS = None      # Size of canvas object
CANVAS_YS = None
CANVAS_X = None      # Current position on canvas
CANVAS_Y = None
CANVAS_COL = None      # Current colour (set to black below)
CANVAS_TSIZE = 12
CANVAS_TSERIFS = 0


def format_color(red, green, blue):
    """Format the color into hexcode"""
    return f'#%02x%02x%02x' % (int(red * 255), int(green * 255), int(blue * 255))


def color_to_vector(color):
    """CHange color to vector"""
    return [int(x, 16) / 256.0 for x in [color[1:3], color[3:5], color[5:7]]]


if WINDOWS:
    CANVAS_tfonts = ['times new roman', 'lucida console']
else:
    CANVAS_tfonts = ['times', 'lucidasans-24']
    # need defaults here


def sleep(secs):
    """
    sleep function for given seconds
    """
    global ROOT_WINDOW
    if ROOT_WINDOW is None:
        time.sleep(secs)
    else:
        ROOT_WINDOW.update_idletasks()
        ROOT_WINDOW.after(int(1000 * secs), ROOT_WINDOW.quit)
        ROOT_WINDOW.mainloop()


def begin_graphics(width=640, height=480,
                   color=format_color(0, 0, 0), title=None):
    """start graphics"""
    global ROOT_WINDOW, CANVAS, CANVAS_X
    global CANVAS_Y, CANVAS_XS, CANVAS_YS, _BG_COLOR

    # Check for duplicate call
    if ROOT_WINDOW is not None:
        # Lose the window.
        ROOT_WINDOW.destroy()

    # Save the canvas size parameters
    CANVAS_XS, CANVAS_YS = width - 1, height - 1
    CANVAS_X, CANVAS_Y = 0, CANVAS_YS
    _BG_COLOR = color

    # Create the root window
    ROOT_WINDOW = tkinter.Tk()
    ROOT_WINDOW.protocol('WM_DELETE_WINDOW', _destroy_window)
    ROOT_WINDOW.title(title or 'Graphics Window')
    ROOT_WINDOW.resizable(0, 0)

    # Create the canvas object
    try:
        CANVAS = tkinter.Canvas(ROOT_WINDOW, width=width, height=height)
        CANVAS.pack()
        draw_background()
        CANVAS.update()
    except Exception:
        ROOT_WINDOW = None
        raise

    # Bind to key-down and key-up events
    ROOT_WINDOW.bind("<KeyPress>", _keypress)
    ROOT_WINDOW.bind("<KeyRelease>", _keyrelease)
    ROOT_WINDOW.bind("<FocusIn>", _clear_keys)
    ROOT_WINDOW.bind("<FocusOut>", _clear_keys)
    ROOT_WINDOW.bind("<Button-1>", _leftclick)
    ROOT_WINDOW.bind("<Button-2>", _rightclick)
    ROOT_WINDOW.bind("<Button-3>", _rightclick)
    ROOT_WINDOW.bind("<Control-Button-1>", _ctrl_leftclick)
    _clear_keys()


_LEFT_CLICK_LOC = None
_RIGHT_CLICK_LOC = None
_CTRL_LEFT_CLICK_LOC = None


def _leftclick(event):
    global _LEFT_CLICK_LOC
    _LEFT_CLICK_LOC = (event.x, event.y)


def _rightclick(event):
    global _RIGHT_CLICK_LOC
    _RIGHT_CLICK_LOC = (event.x, event.y)


def _ctrl_leftclick(event):
    global _CTRL_LEFT_CLICK_LOC
    _CTRL_LEFT_CLICK_LOC = (event.x, event.y)


def wait_for_click():
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
    corners = [(0, 0), (0, CANVAS_YS),
               (CANVAS_XS, CANVAS_YS), (CANVAS_XS, 0)]
    polygon(corners, _BG_COLOR, fillColor=_BG_COLOR,
            filled=True, smoothed=False)


def _destroy_window(event=None):
    sys.exit(0)
#    global ROOT_WINDOW
#    ROOT_WINDOW.destroy()
#    ROOT_WINDOW = None
    # print "DESTROY"


def end_graphics():
    global ROOT_WINDOW, CANVAS, _mouse_enabled
    try:
        try:
            sleep(1)
            if ROOT_WINDOW is not None:
                ROOT_WINDOW.destroy()
        except SystemExit as e:
            print(('Ending graphics raised an exception:', e))
    finally:
        ROOT_WINDOW = None
        CANVAS = None
        _mouse_enabled = 0
        _clear_keys()


def clear_screen(background=None):
    global CANVAS_X, CANVAS_Y
    CANVAS.delete('all')
    draw_background()
    CANVAS_X, CANVAS_Y = 0, CANVAS_YS


def polygon(coords, outlineColor,
            fillColor=None, filled=1,
            smoothed=1, behind=0, width=1):
    c = []
    for coord in coords:
        c.append(coord[0])
        c.append(coord[1])
    if fillColor is None:
        fillColor = outlineColor
    if filled == 0:
        fillColor = ""
    poly = CANVAS.create_polygon(
        c, outline=outlineColor, fill=fillColor, smooth=smoothed, width=width)
    if behind > 0:
        CANVAS.tag_lower(poly, behind)  # Higher should be more visible
    return poly


def square(pos, r, color, filled=1, behind=0):
    x, y = pos
    coords = [(x - r, y - r), (x + r, y - r), (x + r, y + r), (x - r, y + r)]
    return polygon(coords, color, color, filled, 0, behind=behind)


def circle(pos, r,
           outlineColor,
           fillColor,
           endpoints=None,
           style='pieslice',
           width=2):
    x, y = pos
    x0, x1 = x - r - 1, x + r
    y0, y1 = y - r - 1, y + r
    if endpoints is None:
        e = [0, 359]
    else:
        e = list(endpoints)
    while e[0] > e[1]:
        e[1] = e[1] + 360

    return CANVAS.create_arc(x0, y0, x1, y1,
                              outline=outlineColor,
                              fill=fillColor,
                              extent=e[1] - e[0],
                              start=e[0],
                              style=style,
                              width=width)


def image(pos, file="../../blueghost.gif"):
    x, y = pos
    # img = PhotoImage(file=file)
    return CANVAS.create_image(x,
                                y,
                                image=tkinter.PhotoImage(file=file),
                                anchor=tkinter.NW)


def refresh():
    CANVAS.update_idletasks()


def moveCircle(id, pos, r, endpoints=None):
    global CANVAS_X, CANVAS_Y

    x, y = pos
#    x0, x1 = x - r, x + r + 1
#    y0, y1 = y - r, y + r + 1
    x0, _ = x - r - 1, x + r
    y0, _ = y - r - 1, y + r
    if endpoints is None:
        e = [0, 359]
    else:
        e = list(endpoints)
    while e[0] > e[1]:
        e[1] = e[1] + 360

    edit(id, ('start', e[0]), ('extent', e[1] - e[0]))
    move_to(id, x0, y0)


def edit(id, *args):
    CANVAS.itemconfigure(id, **dict(args))


def text(pos,
         color,
         contents,
         font='Helvetica',
         size=12,
         style='normal',
         anchor="nw"):
    global CANVAS_X, CANVAS_Y
    x, y = pos
    font = (font, str(size), style)
    return CANVAS.create_text(x,
                               y,
                               fill=color,
                               text=contents,
                               font=font,
                               anchor=anchor)


def changeText(id, newText, font=None, size=12, style='normal'):
    CANVAS.itemconfigure(id, text=newText)
    if font is not None:
        CANVAS.itemconfigure(id, font=(font, '-%d' % size, style))


def change_color(id, newColor):
    CANVAS.itemconfigure(id, fill=newColor)


def line(here, there, color=format_color(0, 0, 0), width=2):
    x0, y0 = here[0], here[1]
    x1, y1 = there[0], there[1]
    return CANVAS.create_line(x0, y0, x1, y1, fill=color, width=width)


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
    except Exception:
        pass
    _got_release = 1


def remap_arrows(event):
    # TURN ARROW PRESSES INTO LETTERS (SHOULD BE IN KEYBOARD AGENT)
    if event.char in ['a', 's', 'd', 'w']:
        return
    if event.keycode in [37, 101]:  # LEFT ARROW (win / x)
        event.char = 'a'
    if event.keycode in [38, 99]:  # UP ARROW
        event.char = 'w'
    if event.keycode in [39, 102]:  # RIGHT ARROW
        event.char = 'd'
    if event.keycode in [40, 104]:  # DOWN ARROW
        event.char = 's'


def _clear_keys(event=None):
    global _keysdown, _got_release, _keyswaiting
    _keysdown = {}
    _keyswaiting = {}
    _got_release = None


def keys_pressed(d_o_e=None,
                 d_w=tkinter._tkinter.DONT_WAIT):

    if d_o_e is None:
        d_o_e = ROOT_WINDOW.dooneevent
    d_o_e(d_w)
    if _got_release:
        d_o_e(d_w)
    return list(_keysdown.keys())


def keys_waiting():
    global _keyswaiting
    keys = list(_keyswaiting.keys())
    _keyswaiting = {}
    return keys

# Block for a list of keys...


def wait_for_keys():
    keys = []
    while keys == []:
        keys = keys_pressed()
        sleep(0.05)
    return keys


def remove_from_screen(x,
                       d_o_e=None,
                       d_w=tkinter._tkinter.DONT_WAIT):
    if d_o_e is None:
        d_o_e = ROOT_WINDOW.dooneevent
    CANVAS.delete(x)
    d_o_e(d_w)


def _adjust_coords(coord_list, x, y):
    for i in range(0, len(coord_list), 2):
        coord_list[i] = coord_list[i] + x
        coord_list[i + 1] = coord_list[i + 1] + y
    return coord_list


def move_to(object, x, y=None,
            d_o_e=None,
            d_w=tkinter._tkinter.DONT_WAIT):
    if d_o_e is None:
        d_o_e = ROOT_WINDOW.dooneevent
    if y is None:
        try:
            x, y = x
        except Exception as exception:
            raise exception

    horiz = True
    new_coords = []
    current_x, current_y = CANVAS.coords(object)[0:2]  # first point
    for coord in CANVAS.coords(object):
        if horiz:
            inc = x - current_x
        else:
            inc = y - current_y
        horiz = not horiz

        new_coords.append(coord + inc)

    CANVAS.coords(object, *new_coords)
    d_o_e(d_w)


def move_by(object, x_pos, y_pos=None,
            d_o_e=None,
            d_w=tkinter._tkinter.DONT_WAIT, lift=False):
    """Move the pac based on the position"""
    if d_o_e is None:
        d_o_e = ROOT_WINDOW.dooneevent
    if y_pos is None:
        try:
            x_pos, y_pos = x_pos
        except Exception as exc:
            raise exc

    horiz = True
    new_coords = []
    for coord in CANVAS.coords(object):
        if horiz:
            inc = x_pos
        else:
            inc = y_pos
        horiz = not horiz

        new_coords.append(coord + inc)

    CANVAS.coords(object, *new_coords)
    d_o_e(d_w)
    if lift:
        CANVAS.tag_raise(object)


def write_post_script(filename):
    "Writes the current canvas to a postscript file."
    with open(filename, 'w',encoding="utf8") as psfile:
        psfile.write(CANVAS.postscript(pageanchor='sw', y='0.c', x='0.c'))


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
    ghost_shape = [(x * 10 + 20, y * 10 + 20) for x, y in ghost_shape]
    g = polygon(ghost_shape, format_color(1, 1, 1))
    move_to(g, (50, 50))
    circle((150, 150), 20, format_color(0.7, 0.3, 0.0), endpoints=[15, - 15])
    sleep(2)
