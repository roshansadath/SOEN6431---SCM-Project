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
    return '#%02x%02x%02x' % (int(red * 255),
                              int(green * 255),
                              int(blue * 255))


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
    """Left click"""
    global _LEFT_CLICK_LOC
    _LEFT_CLICK_LOC = (event.x, event.y)


def _rightclick(event):
    """control right click"""
    global _RIGHT_CLICK_LOC
    _RIGHT_CLICK_LOC = (event.x, event.y)


def _ctrl_leftclick(event):
    """Control left click"""
    global _CTRL_LEFT_CLICK_LOC
    _CTRL_LEFT_CLICK_LOC = (event.x, event.y)


def wait_for_click():
    """Wait for a click"""
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
    """Draw background"""
    corners = [(0, 0), (0, CANVAS_YS),
               (CANVAS_XS, CANVAS_YS), (CANVAS_XS, 0)]
    polygon(corners, _BG_COLOR, fill_color=_BG_COLOR,
            filled=True, smoothed=False)


def _destroy_window(event=None):
    sys.exit(0)
#    global ROOT_WINDOW
#    ROOT_WINDOW.destroy()
#    ROOT_WINDOW = None
    # print "DESTROY"


def end_graphics():
    """End graphics"""
    global ROOT_WINDOW, CANVAS, _mouse_enabled
    try:
        try:
            sleep(1)
            if ROOT_WINDOW is not None:
                ROOT_WINDOW.destroy()
        except SystemExit as sys_exit:
            print(('Ending graphics raised an exception:', sys_exit))
    finally:
        ROOT_WINDOW = None
        CANVAS = None
        _mouse_enabled = 0
        _clear_keys()


def clear_screen(background=None):
    """Clear screen"""
    global CANVAS_X, CANVAS_Y
    CANVAS.delete('all')
    draw_background()
    CANVAS_X, CANVAS_Y = 0, CANVAS_YS


def polygon(coords, outline_color,
            fill_color=None, filled=1,
            smoothed=1, behind=0, width=1):
    """Draw a polygon"""
    coordss = []
    for coord in coords:
        coordss.append(coord[0])
        coordss.append(coord[1])
    if fill_color is None:
        fill_color = outline_color
    if filled == 0:
        fill_color = ""
    poly = CANVAS.create_polygon(
        coordss, outline=outline_color, fill=fill_color,
        smooth=smoothed, width=width)
    if behind > 0:
        CANVAS.tag_lower(poly, behind)  # Higher should be more visible
    return poly


def square(pos, radius, color, filled=1, behind=0):
    """Draw a square"""
    x_pos, y_pos = pos
    coords = [(x_pos - radius, y_pos - radius),
              (x_pos + radius, y_pos - radius),
              (x_pos + radius, y_pos + radius),
              (x_pos - radius, y_pos + radius)]
    return polygon(coords, color, color, filled, 0, behind=behind)


def circle(pos, radius,
           outline_color,
           fill_color,
           endpoints=None,
           style='pieslice',
           width=2):
    """Draw a circle"""
    x_pos, y_pos = pos
    x0_pos, x1_pos = x_pos - radius - 1, x_pos + radius
    y0_pos, y1_pos = y_pos - radius - 1, y_pos + radius
    if endpoints is None:
        endpoint = [0, 359]
    else:
        endpoint = list(endpoints)
    while endpoint[0] > endpoint[1]:
        endpoint[1] = endpoint[1] + 360

    return CANVAS.create_arc(x0_pos, y0_pos, x1_pos, y1_pos,
                             outline=outline_color,
                             fill=fill_color,
                             extent=endpoint[1] - endpoint[0],
                             start=endpoint[0],
                             style=style,
                             width=width)


def image(pos, file="../../blueghost.gif"):
    """Draw an image"""
    x_pos, y_pos = pos
    # img = PhotoImage(file=file)
    return CANVAS.create_image(x_pos,
                               y_pos,
                               image=tkinter.PhotoImage(file=file),
                               anchor=tkinter.NW)


def refresh():
    """refresh"""
    CANVAS.update_idletasks()


def move_circle(identification, pos, radius, endpoints=None):
    """Move circle"""
    global CANVAS_X, CANVAS_Y

    x_pos, y_pos = pos
#    x0_pos, x1_pos = x_pos - radius, x_pos + radius + 1
#    y0_pos, y1_pos = y_pos - radius, y_pos + radius + 1
    x0_pos, _ = x_pos - radius - 1, x_pos + radius
    y0_pos, _ = y_pos - radius - 1, y_pos + radius
    if endpoints is None:
        endpoint = [0, 359]
    else:
        endpoint = list(endpoints)
    while endpoint[0] > endpoint[1]:
        endpoint[1] = endpoint[1] + 360

    edit(identification, ('start', endpoint[0]),
         ('extent', endpoint[1] - endpoint[0]))
    move_to(identification, x0_pos, y0_pos)


def edit(identification, *args):
    """Edit the item"""
    CANVAS.itemconfigure(identification, **dict(args))


def text(pos,
         color,
         contents,
         font='Helvetica',
         size=12,
         style='normal',
         anchor="nw"):
    """Text"""
    global CANVAS_X, CANVAS_Y
    x_pos, y_pos = pos
    font = (font, str(size), style)
    return CANVAS.create_text(x_pos,
                              y_pos,
                              fill=color,
                              text=contents,
                              font=font,
                              anchor=anchor)


def change_text(identification, new_text, font=None, size=12, style='normal'):
    """Change the text"""
    CANVAS.itemconfigure(identification, text=new_text)
    if font is not None:
        CANVAS.itemconfigure(identification, font=(font,
                                                   f'{size}' % size, style))


def change_color(identification, new_color):
    """Chaneg color"""
    CANVAS.itemconfigure(identification, fill=new_color)


def line(here, there, color=format_color(0, 0, 0), width=2):
    """draw a line"""
    x0_pos, y0_pos = here[0], here[1]
    x1_pos, y1_pos = there[0], there[1]
    return CANVAS.create_line(x0_pos, y0_pos, x1_pos, y1_pos,
                              fill=color, width=width)


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
    except ValueError:
        pass
    _got_release = 1


def remap_arrows(event):
    """Remap the arrows"""
    # TURN ARROW PRESSES INTO LETTERS (SHOULD BE IN KEYBOARD AGENT)
    if event.char in ['a', 's', 'd', 'w']:
        return
    if event.keycode in [37, 101]:  # LEFT ARROW (win / x_pos)
        event.char = 'a'
    if event.keycode in [38, 99]:  # UP ARROW
        event.char = 'w'
    if event.keycode in [39, 102]:  # RIGHT ARROW
        event.char = 'd'
    if event.keycode in [40, 104]:  # DOWN ARROW
        event.char = 's'


def _clear_keys(event=None):
    """CLear keys"""
    global _keysdown, _got_release, _keyswaiting
    _keysdown = {}
    _keyswaiting = {}
    _got_release = None


def keys_pressed(d_o_e=None,
                 d_w=tkinter._tkinter.DONT_WAIT):
    """Keys pressed"""

    if d_o_e is None:
        d_o_e = ROOT_WINDOW.dooneevent
    d_o_e(d_w)
    if _got_release:
        d_o_e(d_w)
    return list(_keysdown.keys())


def keys_waiting():
    """Keys waiting"""
    global _keyswaiting
    keys = list(_keyswaiting.keys())
    _keyswaiting = {}
    return keys

# Block for a list of keys...


def wait_for_keys():
    """Wait for the keys"""
    keys = []
    while not keys:
        keys = keys_pressed()
        sleep(0.05)
    return keys


def remove_from_screen(x_pos,
                       d_o_e=None,
                       d_w=tkinter._tkinter.DONT_WAIT):
    """Remove the screen"""
    if d_o_e is None:
        d_o_e = ROOT_WINDOW.dooneevent
    CANVAS.delete(x_pos)
    d_o_e(d_w)


def _adjust_coords(coord_list, x_pos, y_pos):
    """Adjust coords"""
    for i in range(0, len(coord_list), 2):
        coord_list[i] = coord_list[i] + x_pos
        coord_list[i + 1] = coord_list[i + 1] + y_pos
    return coord_list


def move_to(object, x_pos, y_pos=None,
            d_o_e=None,
            d_w=tkinter._tkinter.DONT_WAIT):
    """Move to a position"""
    if d_o_e is None:
        d_o_e = ROOT_WINDOW.dooneevent
    if y_pos is None:
        try:
            x_pos, y_pos = x_pos
        except Exception as exception:
            raise exception

    horiz = True
    new_coords = []
    current_x, current_y = CANVAS.coords(object)[0:2]  # first point
    for coord in CANVAS.coords(object):
        if horiz:
            inc = x_pos - current_x
        else:
            inc = y_pos - current_y
        horiz = not horiz

        new_coords.append(coord + inc)

    CANVAS.coords(object, *new_coords)
    d_o_e(d_w)


def move_by(pac, x_pos, y_pos=None,
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
    for coord in CANVAS.coords(pac):
        if horiz:
            inc = x_pos
        else:
            inc = y_pos
        horiz = not horiz

        new_coords.append(coord + inc)

    CANVAS.coords(pac, *new_coords)
    d_o_e(d_w)
    if lift:
        CANVAS.tag_raise(pac)


def write_post_script(filename):
    "Writes the current canvas to a postscript file."
    with open(filename, 'w', encoding="utf8") as psfile:
        psfile.write(CANVAS.postscript(pageanchor='sw',
                                       y_pos='0.c', x_pos='0.c'))


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
    ghost_shape = [(x_pos * 10 + 20, y_pos * 10 + 20)
                   for x_pos, y_pos in ghost_shape]
    g = polygon(ghost_shape, format_color(1, 1, 1))
    move_to(g, (50, 50))
    circle((150, 150), 20, format_color(0.7, 0.3, 0.0), endpoints=[15, - 15])
    sleep(2)
