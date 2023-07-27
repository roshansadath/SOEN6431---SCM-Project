""" graphicsDisplay.py
 ------------------
Licensing Information:  You are free to use or extend these projects for
educational purposes provided that (1) you do not distribute or publish
solutions, (2) you retain this notice, and (3) you provide clear
attribution to UC Berkeley, including a link to http://ai.berkeley.edu.

Attribution Information: The Pacman AI projects were developed at UC Berkeley.
The core projects and autograders were primarily created by John DeNero
(denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
Student side autograding was added by Brad Miller, Nick Hay, and
Pieter Abbeel (pabbeel@cs.berkeley.edu)."""

import os
import math
from graphics_utils import write_post_script, line, circle, remove_from_screen
from graphics_utils import format_color, change_color, square
from graphics_utils import refresh, move_circle, end_graphics, change_text
from graphics_utils import edit, move_by, polygon, sleep, begin_graphics
from graphics_utils import text, wait_for_keys, color_to_vector
from game import Directions

###########################
#  GRAPHICS DISPLAY CODE  #
###########################

# Most code by Dan Klein and John Denero
#  written or rewritten
# for cs188, UC Berkeley.
# Some code from a Pacman implementation by LiveWires, and used / modified
# with permission.

DEFAULT_GRID_SIZE = 30.0
INFO_PANE_HEIGHT = 35
BACKGROUND_COLOR = format_color(0, 0, 0)
WALL_COLOR = format_color(0.0 / 255.0, 51.0 / 255.0, 255.0 / 255.0)
INFO_PANE_COLOR = format_color(.4, .4, 0)
SCORE_COLOR = format_color(.9, .9, .9)
PACMAN_OUTLINE_WIDTH = 2
PACMAN_CAPTURE_OUTLINE_WIDTH = 4

GHOST_COLORS = []
GHOST_COLORS.append(format_color(.9, 0, 0))  # Red
GHOST_COLORS.append(format_color(0, .3, .9))  # Blue
GHOST_COLORS.append(format_color(.98, .41, .07))  # Orange
GHOST_COLORS.append(format_color(.1, .75, .7))  # Green
GHOST_COLORS.append(format_color(1.0, 0.6, 0.0))  # Yellow
GHOST_COLORS.append(format_color(.4, 0.13, 0.91))  # Purple

TEAM_COLORS = GHOST_COLORS[:2]

GHOST_SHAPE = [
    (0,    0.3),
    (0.25, 0.75),
    (0.5,  0.3),
    (0.75, 0.75),
    (0.75, -0.5),
    (0.5,  -0.75),
    (-0.5,  -0.75),
    (-0.75, -0.5),
    (-0.75, 0.75),
    (-0.5,  0.3),
    (-0.25, 0.75)
]
GHOST_SIZE = 0.65
SCARED_COLOR = format_color(1, 1, 1)

GHOST_VEC_COLORS = list(map(color_to_vector, GHOST_COLORS))

PACMAN_COLOR = format_color(255.0 / 255.0, 255.0 / 255.0, 61.0 / 255)
PACMAN_SCALE = 0.5
# pacman_speed = 0.25

# Food
FOOD_COLOR = format_color(1, 1, 1)
FOOD_SIZE = 0.1

# Laser
LASER_COLOR = format_color(1, 0, 0)
LASER_SIZE = 0.02

# Capsule graphics
CAPSULE_COLOR = format_color(1, 1, 1)
CAPSULE_SIZE = 0.25

# Drawing walls
WALL_RADIUS = 0.15


class info_pane:
    """INFO PANE"""

    def __init__(self, layout, grid_size):
        self.grid_size = grid_size
        self.width = (layout.width) * grid_size
        self.base = (layout.height + 1) * grid_size
        self.height = INFO_PANE_HEIGHT
        self.font_size = 24
        self.text_color = PACMAN_COLOR
        self.draw_pane()

    def to_screen(self, pos, y_pos=None):
        """
          Translates a point relative from the bottom left of the info pane.
        """
        if y_pos is None:
            x_pos, y_pos = pos
        else:
            x_pos = pos

        x_pos = self.grid_size + x_pos  # Margin
        y_pos = self.base + y_pos
        return x_pos, y_pos

    def draw_pane(self):
        """Draw pane"""
        self.score_text = text(self.to_screen(
            0, 0), self.text_color, "SCORE:    0",
            "Times",
            self.font_size,
            "bold")

    def initialize_ghost_distances(self, distances):
        """Inintialize Ghost distance"""
        self.ghost_distance_text = []

        size = 20
        if self.width < 240:
            size = 12
        if self.width < 160:
            size = 10

        for i, distance in enumerate(distances):
            itext = text(self.to_screen(self.width / 2 +
                                   self.width / 8 * i, 0),
                     GHOST_COLORS[i + 1], distance, "Times", size, "bold")
            self.ghost_distance_text.append(itext)

    def update_score(self, score):
        """Update score"""
        change_text(self.score_text, f"SCORE: {score}")

    def set_team(self, is_blue):
        """set team"""
        ntext = "RED TEAM"
        if is_blue:
            ntext = "BLUE TEAM"
        self.team_text = text(self.to_screen(
            300, 0), self.text_color, ntext, "Times", self.font_size, "bold")

    def update_ghost_distances(self, distances):
        """Update ghost distances"""
        if len(distances) == 0:
            return
        if 'ghost_distance_text' not in dir(self):
            self.initialize_ghost_distances(distances)
        else:
            for i, distance in enumerate(distances):
                change_text(self.ghost_distance_text[i], distance)

    def draw_ghost(self):
        """Draw ghosts"""
        pass

    def draw_pacman(self):
        """Draw pacman"""
        pass

    def draw_warning(self):
        """Draw warning"""
        pass

    def clear_icon(self):
        """Clear icon"""
        pass

    def update_message(self, message):
        """Update message"""
        pass

    def clear_message(self):
        """Clear message"""
        pass

class PacmanGraphics:
    """pacman graphics"""
    def __init__(self, zoom=1.0, frame_time=0.0, capture=False):
        self.havewindow = 0
        self.current_ghost_images = {}
        self.pacman_image = None
        self.zoom = zoom
        self.grid_size = DEFAULT_GRID_SIZE * zoom
        self.capture = capture
        self.frame_time = frame_time

    def check_null_display(self):
        """Check display"""
        return False

    def initialize(self, state, is_blue=False):
        """Initialize"""
        self.is_blue = is_blue
        self.start_graphics(state)

        # self.draw_distributions(state)
        self.distribution_images = None  # Initialized lazily
        self.draw_static_objects(state)
        self.draw_agent_objects(state)

        # Information
        self.previous_state = state

    def start_graphics(self, state):
        """start graphics"""
        self.layout = state.layout
        layout = self.layout
        self.width = layout.width
        self.height = layout.height
        self.makewindow(self.width, self.height)
        self.info_pane = info_pane(layout, self.grid_size)
        self.current_state = layout

    def draw_distributions(self, state):
        """draw distributions"""
        walls = state.layout.walls
        dist = []
        for x_pos in range(walls.width):
            distx = []
            dist.append(distx)
            for y_pos in range(walls.height):
                screen_x, screen_y = self.to_screen((x_pos, y_pos))
                block = square((screen_x, screen_y),
                               0.5 * self.grid_size,
                               color=BACKGROUND_COLOR,
                               filled=1, behind=2)
                distx.append(block)
        self.distribution_images = dist

    def draw_static_objects(self, state):
        """draw static object"""
        layout = self.layout
        self.draw_walls(layout.walls)
        self.food = self.draw_food(layout.food)
        self.capsules = self.draw_capsules(layout.capsules)
        refresh()

    def draw_agent_objects(self, state):
        """Draw agent obeject"""
        self.agent_images = []  # (agent_state, image)
        for index, agent in enumerate(state.agent_states):
            if agent.is_pacman:
                image = self.draw_pacman(agent, index)
                self.agent_images.append((agent, image))
            else:
                image = self.draw_ghost(agent, index)
                self.agent_images.append((agent, image))
        refresh()

    def swap_images(self, agent_index, new_state):
        """
          Changes an image from a ghost to a pacman or vis versa (for capture)
        """
        _, prev_image = self.agent_images[agent_index]
        for item in prev_image:
            remove_from_screen(item)
        if new_state.is_pacman:
            image = self.draw_pacman(new_state, agent_index)
            self.agent_images[agent_index] = (new_state, image)
        else:
            image = self.draw_ghost(new_state, agent_index)
            self.agent_images[agent_index] = (new_state, image)
        refresh()

    def update(self, new_state):
        """update to new state"""
        agent_index = new_state.agent_moved
        agent_state = new_state.agent_states[agent_index]

        if self.agent_images[agent_index][0].is_pacman != agent_state.is_pacman:
            self.swap_images(agent_index, agent_state)
        prev_state, prev_image = self.agent_images[agent_index]
        if agent_state.is_pacman:
            self.animate_pacman(agent_state, prev_state, prev_image)
        else:
            self.move_ghost(agent_state, agent_index, prev_state, prev_image)
        self.agent_images[agent_index] = (agent_state, prev_image)

        if new_state.food_eaten is not None:
            self.remove_food(new_state.food_eaten, self.food)
        if new_state.capsule_eaten is not None:
            self.remove_capsule(new_state.capsule_eaten, self.capsules)
        self.info_pane.update_score(new_state.score)
        if 'ghostDistances' in dir(new_state):
            self.info_pane.update_ghost_distances(new_state.ghostDistances)

    def makewindow(self, width, height):
        """make window"""
        grid_width = (width - 1) * self.grid_size
        grid_height = (height - 1) * self.grid_size
        screen_width = 2 * self.grid_size + grid_width
        screen_height = 2 * self.grid_size + grid_height + INFO_PANE_HEIGHT

        begin_graphics(screen_width,
                       screen_height,
                       BACKGROUND_COLOR,
                       "CS188 Pacman")

    def draw_pacman(self, pacman, index):
        """draw pacman"""
        position = self.get_position(pacman)
        screen_point = self.to_screen(position)
        endpoints = self.get_endpoints(self.get_direction(pacman))

        width = PACMAN_OUTLINE_WIDTH
        outline_color = PACMAN_COLOR
        fill_color = PACMAN_COLOR

        if self.capture:
            outline_color = TEAM_COLORS[index % 2]
            fill_color = GHOST_COLORS[index]
            width = PACMAN_CAPTURE_OUTLINE_WIDTH

        return [circle(screen_point, PACMAN_SCALE * self.grid_size,
                       fill_color=fill_color, outline_color=outline_color,
                       endpoints=endpoints,
                       width=width)]

    def get_endpoints(self, direction, position=(0, 0)):
        """Get endpoints"""
        x_pos, y_pos = position
        pos = x_pos - int(x_pos) + y_pos - int(y_pos)
        width = 30 + 80 * math.sin(math.pi * pos)

        delta = width / 2
        if direction == 'West':
            endpoints = (180 + delta, 180 - delta)
        elif direction == 'North':
            endpoints = (90 + delta, 90 - delta)
        elif direction == 'South':
            endpoints = (270 + delta, 270 - delta)
        else:
            endpoints = (0 + delta, 0 - delta)
        return endpoints

    def move_pacman(self, position, direction, image):
        """Move pacman"""
        screen_position = self.to_screen(position)
        endpoints = self.get_endpoints(direction, position)
        scale = PACMAN_SCALE * self.grid_size
        move_circle(image[0], screen_position, scale, endpoints)
        refresh()

    def animate_pacman(self, pacman, prev_pacman, image):
        """animate pacman"""
        if self.frame_time < 0:
            print('Press any key to step forward, "q" to play')
            keys = wait_for_keys()
            if 'q' in keys:
                self.frame_time = 0.1
        if self.frame_time > 0.01 or self.frame_time < 0:
            from_x, from_y = self.get_position(prev_pacman)
            p_x, p_y = self.get_position(pacman)
            frames = 4.0
            for i in range(1, int(frames) + 1):
                pos = p_x * i / frames + from_x * \
                    (frames - i) / frames, p_y * i / \
                    frames + from_y * (frames - i) / frames
                self.move_pacman(pos, self.get_direction(pacman), image)
                refresh()
                sleep(abs(self.frame_time) / frames)
        self.move_pacman(self.get_position(pacman),
                            self.get_direction(pacman), image)
        refresh()

    def get_ghost_color(self, ghost, ghost_index):
        """Get ghost color"""
        if ghost.scared_timer > 0:
            return SCARED_COLOR
        return GHOST_COLORS[ghost_index]

    def draw_ghost(self, ghost, agent_index):
        """draw ghost"""
        pos = self.get_position(ghost)
        direction = self.get_direction(ghost)
        screen_x, screen_y = self.to_screen(pos)
        coords = []
        for (x_pos, y_pos) in GHOST_SHAPE:
            coords.append((x_pos * self.grid_size * GHOST_SIZE + screen_x,
                           y_pos * self.grid_size * GHOST_SIZE + screen_y))

        colour = self.get_ghost_color(ghost, agent_index)
        boderivative_y = polygon(coords, colour, filled=1)
        white = format_color(1.0, 1.0, 1.0)
        black = format_color(0.0, 0.0, 0.0)

        derivative_x = 0
        derivative_y = 0
        if direction == 'North':
            derivative_y = -0.2
        if direction == 'South':
            derivative_y = 0.2
        if direction == 'East':
            derivative_x = 0.2
        if direction == 'West':
            derivative_x = -0.2
        left_eye = circle((screen_x + self.grid_size *
                          GHOST_SIZE *
                          (-0.3 + derivative_x / 1.5), screen_y -
                          self.grid_size *
                          GHOST_SIZE *
                          (0.3 - derivative_y / 1.5)), self.grid_size *
                         GHOST_SIZE *
                         0.2, white, white)
        right_eye = circle((screen_x + self.grid_size *
                           GHOST_SIZE *
                           (0.3 + derivative_x / 1.5), screen_y -
                           self.grid_size *
                           GHOST_SIZE *
                           (0.3 - derivative_y / 1.5)), self.grid_size *
                          GHOST_SIZE *
                          0.2, white, white)
        left_pupil = circle((screen_x + self.grid_size *
                            GHOST_SIZE *
                            (-0.3 + derivative_x), screen_y -
                            self.grid_size *
                            GHOST_SIZE *
                            (0.3 - derivative_y)), self.grid_size *
                           GHOST_SIZE *
                           0.08, black, black)
        right_pupil = circle((screen_x + self.grid_size *
                             GHOST_SIZE *
                             (0.3 + derivative_x), screen_y -
                             self.grid_size *
                             GHOST_SIZE *
                             (0.3 - derivative_y)), self.grid_size *
                            GHOST_SIZE *
                            0.08, black, black)
        ghost_image_parts = []
        ghost_image_parts.append(boderivative_y)
        ghost_image_parts.append(left_eye)
        ghost_image_parts.append(right_eye)
        ghost_image_parts.append(left_pupil)
        ghost_image_parts.append(right_pupil)

        return ghost_image_parts

    def move_eyes(self, pos, direction, eyes):
        """move eyes"""
        screen_x, screen_y = self.to_screen(pos)
        derivative_x = 0
        derivative_y = 0
        if direction == 'North':
            derivative_y = -0.2
        if direction == 'South':
            derivative_y = 0.2
        if direction == 'East':
            derivative_x = 0.2
        if direction == 'West':
            derivative_x = -0.2
        move_circle(eyes[0],
                   (screen_x + self.grid_size * GHOST_SIZE * (-0.3 + derivative_x / 1.5),
                    screen_y -
                    self.grid_size * GHOST_SIZE * (0.3 - derivative_y / 1.5)),
                   self.grid_size * GHOST_SIZE * 0.2)
        move_circle(eyes[1],
                   (screen_x + self.grid_size * GHOST_SIZE * (0.3 + derivative_x / 1.5),
                    screen_y -
                    self.grid_size * GHOST_SIZE * (0.3 - derivative_y / 1.5)),
                   self.grid_size * GHOST_SIZE * 0.2)
        move_circle(eyes[2],
                   (screen_x + self.grid_size * GHOST_SIZE * (-0.3 + derivative_x),
                    screen_y -
                    self.grid_size * GHOST_SIZE * (0.3 - derivative_y)),
                   self.grid_size * GHOST_SIZE * 0.08)
        move_circle(eyes[3],
                   (screen_x + self.grid_size * GHOST_SIZE * (0.3 + derivative_x),
                    screen_y -
                    self.grid_size * GHOST_SIZE * (0.3 - derivative_y)),
                   self.grid_size * GHOST_SIZE * 0.08)

    def move_ghost(self, ghost, ghost_index, prev_ghost, ghost_image_parts):
        """Move ghosts"""
        old_x, old_y = self.to_screen(self.get_position(prev_ghost))
        new_x, new_y = self.to_screen(self.get_position(ghost))
        delta = new_x - old_x, new_y - old_y

        for ghost_image_part in ghost_image_parts:
            move_by(ghost_image_part, delta)
        refresh()

        if ghost.scared_timer > 0:
            color = SCARED_COLOR
        else:
            color = GHOST_COLORS[ghost_index]
        edit(ghost_image_parts[0], ('fill', color), ('outline', color))
        self.move_eyes(self.get_position(ghost),
                      self.get_direction(ghost), ghost_image_parts[-4:])
        refresh()

    def get_position(self, agent_state):
        """Get position of pac"""
        if agent_state.configuration is None:
            return (-1000, -1000)
        return agent_state.get_position()

    def get_direction(self, agent_state):
        """Get the direction"""
        if agent_state.configuration is None:
            return Directions.STOP
        return agent_state.configuration.get_direction()

    def finish(self):
        """End the graphics"""
        end_graphics()

    def to_screen(self, point):
        """to screen"""
        (x_pos, y_pos) = point
        # y_pos = self.height - y_pos
        x_pos = (x_pos + 1) * self.grid_size
        y_pos = (self.height - y_pos) * self.grid_size
        return (x_pos, y_pos)

    # Fixes some TK issue with off-center circles
    def to_screen2(self, point):
        """to screen2"""
        (x_pos, y_pos) = point
        # y_pos = self.height - y_pos
        x_pos = (x_pos + 1) * self.grid_size
        y_pos = (self.height - y_pos) * self.grid_size
        return (x_pos, y_pos)

    def draw_walls(self, wall_matrix):
        """draw walls"""
        wall_color = WALL_COLOR
        for x_num, x_pos in enumerate(wall_matrix):
            if self.capture and (x_num * 2) < wall_matrix.width:
                wall_color = TEAM_COLORS[0]
            if self.capture and (x_num * 2) >= wall_matrix.width:
                wall_color = TEAM_COLORS[1]

            for y_num, cell in enumerate(x_pos):
                if cell:  # There's a wall here
                    pos = (x_num, y_num)
                    screen = self.to_screen(pos)
                    screen2 = self.to_screen2(pos)

                    # draw each quadrant of the square based on adjacent walls
                    w_is_wall = self.is_wall(x_num - 1, y_num, wall_matrix)
                    e_is_wall = self.is_wall(x_num + 1, y_num, wall_matrix)
                    n_is_wall = self.is_wall(x_num, y_num + 1, wall_matrix)
                    sis_wall = self.is_wall(x_num, y_num - 1, wall_matrix)
                    nw_is_wall = self.is_wall(x_num - 1, y_num + 1, wall_matrix)
                    sw_is_wall = self.is_wall(x_num - 1, y_num - 1, wall_matrix)
                    ne_is_wall = self.is_wall(x_num + 1, y_num + 1, wall_matrix)
                    se_is_wall = self.is_wall(x_num + 1, y_num - 1, wall_matrix)

                    # NE quadrant
                    if (not n_is_wall) and (not e_is_wall):
                        # inner circle
                        circle(screen2, WALL_RADIUS * self.grid_size,
                               wall_color, wall_color, (0, 91), 'arc')
                    if (n_is_wall) and (not e_is_wall):
                        # vertical line
                        line(add(screen, (self.grid_size * WALL_RADIUS, 0)),
                             add(screen, (self.grid_size * WALL_RADIUS,
                                          self.grid_size * (-0.5) - 1)),
                             wall_color)
                    if (not n_is_wall) and (e_is_wall):
                        # horizontal line
                        line(add(screen,
                                 (0,
                                  self.grid_size * (-1) * WALL_RADIUS)),
                             add(screen,
                                 (self.grid_size * 0.5 + 1,
                                  self.grid_size * (-1) * WALL_RADIUS)),
                             wall_color)
                    if (n_is_wall) and (e_is_wall) and (not ne_is_wall):
                        # outer circle
                        circle(add(screen2,
                                   (self.grid_size * 2 * WALL_RADIUS,
                                    self.grid_size * (-2) * WALL_RADIUS)),
                               WALL_RADIUS * self.grid_size - 1,
                               wall_color,
                               wall_color,
                               (180,
                                271),
                               'arc')
                        line(add(screen,
                                 (self.grid_size * 2 * WALL_RADIUS - 1,
                                  self.grid_size * (-1) * WALL_RADIUS)),
                             add(screen,
                                 (self.grid_size * 0.5 + 1,
                                  self.grid_size * (-1) * WALL_RADIUS)),
                             wall_color)
                        line(add(screen,
                                 (self.grid_size * WALL_RADIUS,
                                  self.grid_size * (-2) * WALL_RADIUS + 1)),
                             add(screen,
                                 (self.grid_size * WALL_RADIUS,
                                  self.grid_size * (-0.5))),
                             wall_color)

                    # NW quadrant
                    if (not n_is_wall) and (not w_is_wall):
                        # inner circle
                        circle(screen2,
                               WALL_RADIUS * self.grid_size,
                               wall_color, wall_color, (90, 181), 'arc')
                    if (n_is_wall) and (not w_is_wall):
                        # vertical line
                        line(add(screen,
                                 (self.grid_size * (-1) * WALL_RADIUS,
                                  0)),
                             add(screen,
                                 (self.grid_size * (-1) * WALL_RADIUS,
                                  self.grid_size * (-0.5) - 1)),
                             wall_color)
                    if (not n_is_wall) and (w_is_wall):
                        # horizontal line
                        line(add(screen,
                                 (0,
                                  self.grid_size * (-1) * WALL_RADIUS)),
                             add(screen,
                                 (self.grid_size * (-0.5) - 1,
                                  self.grid_size * (-1) * WALL_RADIUS)),
                             wall_color)
                    if (n_is_wall) and (w_is_wall) and (not nw_is_wall):
                        # outer circle
                        circle(add(screen2,
                                   (self.grid_size * (-2) * WALL_RADIUS,
                                    self.grid_size * (-2) * WALL_RADIUS)),
                               WALL_RADIUS * self.grid_size - 1,
                               wall_color,
                               wall_color,
                               (270,
                                361),
                               'arc')
                        line(add(screen,
                                 (self.grid_size * (-2) * WALL_RADIUS + 1,
                                  self.grid_size * (-1) * WALL_RADIUS)),
                             add(screen,
                                 (self.grid_size * (-0.5),
                                  self.grid_size * (-1) * WALL_RADIUS)),
                             wall_color)
                        line(add(screen,
                                 (self.grid_size * (-1) * WALL_RADIUS,
                                  self.grid_size * (-2) * WALL_RADIUS + 1)),
                             add(screen,
                                 (self.grid_size * (-1) * WALL_RADIUS,
                                  self.grid_size * (-0.5))),
                             wall_color)

                    # SE quadrant
                    if (not sis_wall) and (not e_is_wall):
                        # inner circle
                        circle(screen2,
                               WALL_RADIUS * self.grid_size,
                               wall_color, wall_color, (270, 361), 'arc')
                    if (sis_wall) and (not e_is_wall):
                        # vertical line
                        line(add(screen,
                                 (self.grid_size * WALL_RADIUS, 0)),
                             add(screen,
                                 (self.grid_size * WALL_RADIUS,
                                  self.grid_size * (0.5) + 1)), wall_color)
                    if (not sis_wall) and (e_is_wall):
                        # horizontal line
                        line(add(screen,
                                 (0, self.grid_size * (1) * WALL_RADIUS)),
                             add(screen,
                                 (self.grid_size * 0.5 + 1,
                                  self.grid_size * (1) * WALL_RADIUS)),
                             wall_color)
                    if (sis_wall) and (e_is_wall) and (not se_is_wall):
                        # outer circle
                        circle(add(screen2,
                                   (self.grid_size * 2 * WALL_RADIUS,
                                    self.grid_size * (2) * WALL_RADIUS)),
                               WALL_RADIUS * self.grid_size - 1,
                               wall_color, wall_color,
                               (90, 181), 'arc')
                        line(add(screen, (self.grid_size * 2 * WALL_RADIUS - 1,
                                          self.grid_size * (1) * WALL_RADIUS)),
                             add(screen, (self.grid_size * 0.5,
                                          self.grid_size * (1) * WALL_RADIUS)),
                             wall_color)
                        line(add(screen,
                                 (self.grid_size * WALL_RADIUS,
                                  self.grid_size * (2) * WALL_RADIUS-1)),
                             add(screen,
                                 (self.grid_size * WALL_RADIUS,
                                  self.grid_size * (0.5))), wall_color)

                    # SW quadrant
                    if (not sis_wall) and (not w_is_wall):
                        # inner circle
                        circle(screen2, WALL_RADIUS * self.grid_size,
                               wall_color, wall_color, (180, 271), 'arc')
                    if (sis_wall) and (not w_is_wall):
                        # vertical line
                        line(add(screen, (self.grid_size * (-1) * WALL_RADIUS,
                                          0)),
                             add(screen, (self.grid_size * (-1) * WALL_RADIUS,
                                          self.grid_size*(0.5)+1)), wall_color)
                    if (not sis_wall) and (w_is_wall):
                        # horizontal line
                        line(add(screen, (0, self.grid_size*(1)*WALL_RADIUS)),
                             add(screen, (self.grid_size * (-0.5) - 1,
                                          self.grid_size * (1) *
                                          WALL_RADIUS)), wall_color)
                    if (sis_wall) and (w_is_wall) and (not sw_is_wall):
                        # outer circle
                        circle(add(screen2, (self.grid_size * (-2)*WALL_RADIUS,
                                             self.grid_size * (2)*WALL_RADIUS)),
                               WALL_RADIUS * self.grid_size - 1,
                               wall_color, wall_color, (0, 91), 'arc')
                        line(add(screen, (self.grid_size * (-2) * WALL_RADIUS+1,
                                          self.grid_size * (1) * WALL_RADIUS)),
                             add(screen, (self.grid_size * (-0.5),
                                          self.grid_size * (1) *
                                          WALL_RADIUS)), wall_color)
                        line(add(screen, (self.grid_size * (-1) * WALL_RADIUS,
                                          self.grid_size * (2) * WALL_RADIUS - 1
                                          )),
                             add(screen, (self.grid_size * (-1) * WALL_RADIUS,
                                          self.grid_size * (0.5))), wall_color)

    def is_wall(self, x_pos, y_pos, walls):
        """is wall"""
        if x_pos < 0 or y_pos < 0:
            return False
        if x_pos >= walls.width or y_pos >= walls.height:
            return False
        return walls[x_pos][y_pos]

    def draw_food(self, food_matrix):
        """Draw food"""
        food_images = []
        color = FOOD_COLOR
        for x_num, x_pos in enumerate(food_matrix):
            if self.capture and (x_num * 2) <= food_matrix.width:
                color = TEAM_COLORS[0]
            if self.capture and (x_num * 2) > food_matrix.width:
                color = TEAM_COLORS[1]
            image_row = []
            food_images.append(image_row)
            for y_num, cell in enumerate(x_pos):
                if cell:  # There's food here
                    screen = self.to_screen((x_num, y_num))
                    dot = circle(screen,
                                 FOOD_SIZE * self.grid_size,
                                 outline_color=color, fill_color=color,
                                 width=1)
                    image_row.append(dot)
                else:
                    image_row.append(None)
        return food_images

    def draw_capsules(self, capsules):
        """Draw capsules"""
        capsule_images = {}
        for capsule in capsules:
            (screen_x, screen_y) = self.to_screen(capsule)
            dot = circle((screen_x, screen_y),
                         CAPSULE_SIZE * self.grid_size,
                         outline_color=CAPSULE_COLOR,
                         fill_color=CAPSULE_COLOR,
                         width=1)
            capsule_images[capsule] = dot
        return capsule_images

    def remove_food(self, cell, food_images):
        """Remove food"""
        x_pos, y_pos = cell
        remove_from_screen(food_images[x_pos][y_pos])

    def remove_capsule(self, cell, capsule_images):
        """Remove capsule"""
        x_pos, y_pos = cell
        remove_from_screen(capsule_images[(x_pos, y_pos)])

    def drawexpanded_cells(self, cells):
        """
        Draws an overlay of expanded grid positions for search agents
        """
        n_cells = float(len(cells))
        base_color = [1.0, 0.0, 0.0]
        self.clearexpanded_cells()
        self.expanded_cells = []
        for k, cell in enumerate(cells):
            screen_pos = self.to_screen(cell)
            cell_color = format_color(
                *[(n_cells - k) * color * .5 / n_cells + .25 for color in base_color])
            block = square(screen_pos,
                           0.5 * self.grid_size,
                           color=cell_color,
                           filled=1, behind=2)
            self.expanded_cells.append(block)
            if self.frame_time < 0:
                refresh()

    def clearexpanded_cells(self):
        """Clear expanded cells"""
        if 'expanded_cells' in dir(self) and len(self.expanded_cells) > 0:
            for cell in self.expanded_cells:
                remove_from_screen(cell)

    def update_distributions(self, distributions):
        """Draws an agent's belief distributions"""
        # copy all distributions so we don't change their state
        distributions = [x_pos.copy() for x_pos in distributions]
        if self.distribution_images is None:
            self.draw_distributions(self.previous_state)
        for _,x_pos in enumerate(len(self.distribution_images)):
            for y_pos in range(len(self.distribution_images[0])):
                image = self.distribution_images[x_pos][y_pos]
                weights = [dist[(x_pos, y_pos)] for dist in distributions]

                if sum(weights) != 0:
                    pass
                # Fog of war
                color = [0.0, 0.0, 0.0]
                colors = GHOST_VEC_COLORS[1:]  # With Pacman
                if self.capture:
                    colors = GHOST_VEC_COLORS
                for weight, gcolor in zip(weights, colors):
                    color = [min(1.0, c + 0.95 * g * weight ** .3)
                             for c, g in zip(color, gcolor)]
                change_color(image, format_color(*color))
        refresh()


class FirstPersonPacmanGraphics(PacmanGraphics):
    """First pacman graphics"""
    def __init__(self, zoom=1.0, show_ghosts=True, capture=False, frame_time=0):
        PacmanGraphics.__init__(self, zoom, frame_time=frame_time)
        self.show_ghosts = show_ghosts
        self.capture = capture

    def initialize(self, state, is_blue=False):

        self.is_blue = is_blue
        PacmanGraphics.start_graphics(self, state)
        # Initialize distribution images
        self.layout = state.layout

        # Draw the rest
        self.distribution_images = None  # initialize lazily
        self.draw_static_objects(state)
        self.draw_agent_objects(state)

        # Information
        self.previous_state = state

    def look_ahead(self, config, state):
        """Check directions"""
        if config.get_direction() == 'Stop':
            return
        pass
        # Draw relevant ghosts
        all_ghosts = state.getGhostStates()
        visible_ghosts = state.getvisible_ghosts()
        for i, ghost in enumerate(all_ghosts):
            if ghost in visible_ghosts:
                self.draw_ghost(ghost, i)
            else:
                self.current_ghost_images[i] = None

    def get_ghost_color(self, ghost, ghost_index):
        """GEt ghost color"""
        return GHOST_COLORS[ghost_index]

    def get_position(self, ghostState):
        """get ghost position"""
        flag1 = self.show_ghosts and not ghostState.is_pacman
        flag2 = ghostState.get_position()[1] > 1
        if not flag1 and flag2:
            return (-1000, -1000)
        return PacmanGraphics.get_position(self, ghostState)


def add(x_pos, y_pos):
    """Add pos"""
    return (x_pos[0] + y_pos[0], x_pos[1] + y_pos[1])


# Saving graphical output
# -----------------------
# Note: to make an animated gif from this postscript output, try the command:
# convert -delay 7 -loop 1 -compress lzw -layers optimize frame* out.gif
# convert is part of imagemagick (freeware)

SAVE_POSTSCRIPT = False
POSTSCRIPT_OUTPUT_DIR = 'frames'
FRAME_NUMBER = 0


def saveFrame():
    "Saves the current graphical output as a postscript file"
    global SAVE_POSTSCRIPT, FRAME_NUMBER, POSTSCRIPT_OUTPUT_DIR
    if not SAVE_POSTSCRIPT:
        return
    if not os.path.exists(POSTSCRIPT_OUTPUT_DIR):
        os.mkdir(POSTSCRIPT_OUTPUT_DIR)
    name = os.path.join(POSTSCRIPT_OUTPUT_DIR, 'frame_%08d.ps' % FRAME_NUMBER)
    FRAME_NUMBER += 1
    write_post_script(name)  # writes the current canvas
