""" layout.py
# ---------
Licensing Information:  You are free to use or extend these projects for
educational purposes provided that (1) you do not distribute or publish
solutions, (2) you retain this notice, and (3) you provide clear
attribution to UC Berkeley, including a link to http://ai.berkeley.edu.

Attribution Information: The Pacman AI projects were developed at UC Berkeley.
The core projects and autograders were primarily created by John DeNero
(denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
Student side autograding was added by Brad Miller, Nick Hay, and
Pieter Abbeel (pabbeel@cs.berkeley.edu)."""


import random
import os
from functools import reduce
from game import Directions
from util import manhattanDistance
from game import Grid

VISIBILITY_MATRIX_CACHE = {}


class Layout:
    """
    A Layout manages the static information about the game board.
    """

    def __init__(self, layout_text):
        self.width = len(layout_text[0])
        self.height = len(layout_text)
        self.walls = Grid(self.width, self.height, False)
        self.food = Grid(self.width, self.height, False)
        self.capsules = []
        self.agent_positions = []
        self.num_ghosts = 0
        self.process_layout_text(layout_text)
        self.layout_text = layout_text
        self.totalFood = len(self.food.asList())

        # self.initializeVisibilityMatrix()

    def get_num_ghosts(self):
        return self.num_ghosts

    def initializeVisibilityMatrix(self):
        global VISIBILITY_MATRIX_CACHE 
        if reduce(str.__add__, self.layout_text) not in VISIBILITY_MATRIX_CACHE:
            vecs = [(-0.5, 0), (0.5, 0), (0, -0.5), (0, 0.5)]
            dirs = [Directions.NORTH, Directions.SOUTH,
                    Directions.WEST, Directions.EAST]
            vis = Grid(self.width, self.height, {Directions.NORTH: set(),
                                                 Directions.SOUTH: set(
            ), Directions.EAST: set(), Directions.WEST: set(),
                Directions.STOP: set()})
            for x_width in range(self.width):
                for y_height in range(self.height):
                    if self.walls[x_width][y_height] is False:
                        for vec, direction in zip(vecs, dirs):
                            derivative_x, derivative_y = vec
                            nextx, nexty = x_width + derivative_x, y_height + derivative_y
                            cond1 = (nextx + nexty) != int(nextx) + int(nexty)
                            cond2 = self.walls[int(nextx)][int(nexty)]
                            while cond1 or not cond2:
                                vis[x_width][y_height][direction].add((nextx, nexty))
                                nextx, nexty = x_width + derivative_x, y_height + derivative_y
            self.visibility = vis
            VISIBILITY_MATRIX_CACHE[reduce(str.__add__, self.layout_text)] = vis
        else:
            self.visibility = VISIBILITY_MATRIX_CACHE[
                reduce(str.__add__, self.layout_text)]

    def is_wall(self, pos):
        """Check if it is a wall at specific position"""
        x_index, col = pos
        return self.walls[x_index][col]

    def get_random_legal_position(self):
        """Get the legal position for the pac"""
        x_corner = random.choice(list(range(self.width)))
        y_corner = random.choice(list(range(self.height)))
        while self.is_wall((x_corner, y_corner)):
            x_corner = random.choice(list(range(self.width)))
            y_corner = random.choice(list(range(self.height)))
        return (x_corner, y_corner)

    def get_random_corner(self):
        """Get random corner of the canvas"""
        poses = [(1, 1), (1, self.height - 2), (self.width - 2, 1),
                 (self.width - 2, self.height - 2)]
        return random.choice(poses)

    def get_furthest_corner(self, pac_pos):
        """Get the furthest corner from current position"""
        poses = [(1, 1), (1, self.height - 2), (self.width - 2, 1),
                 (self.width - 2, self.height - 2)]
        _ , pos = max([(manhattanDistance(p, pac_pos), p) for p in poses])
        return pos

    def is_visible_from(self, ghost_pos, pac_pos, pac_direction):
        """Check the visibility of the ghost"""
        row, col = [int(x) for x in pac_pos]
        return ghost_pos in self.visibility[row][col][pac_direction]

    def __str__(self):
        return "\n".join(self.layout_text)

    def deep_copy(self):
        """Call layout function"""
        return Layout(self.layout_text[:])

    def process_layout_text(self, layout_text):
        """
        Coordinates are flipped from the input format to the (x,y)
        convention here

        The shape of the maze.  Each character
        represents a different type of object.
         % - Wall
         . - Food
         o - Capsule
         G - Ghost
         P - Pacman
        Other characters are ignored.
        """
        max_y = self.height - 1
        for y_height in range(self.height):
            for x_width in range(self.width):
                layout_char = layout_text[max_y - y_height][x_width]
                self.process_layout_char(x_width, y_height, layout_char)
        self.agent_positions.sort()
        self.agent_positions = [(i == 0, pos) for i, pos in self.agent_positions]

    def process_layout_char(self, x_pos, y_pos, layout_char):
        """Process the layout characters"""
        if layout_char == '%':
            self.walls[x_pos][y_pos] = True
        elif layout_char == '.':
            self.food[x_pos][y_pos] = True
        elif layout_char == 'o':
            self.capsules.append((x_pos, y_pos))
        elif layout_char == 'P':
            self.agent_positions.append((0, (x_pos, y_pos)))
        elif layout_char in ['G']:
            self.agent_positions.append((1, (x_pos, y_pos)))
            self.num_ghosts += 1
        elif layout_char in ['1', '2', '3', '4']:
            self.agent_positions.append((int(layout_char), (x_pos, y_pos)))
            self.num_ghosts += 1


def get_layout(name, back=2):
    """Get the layout for the game"""
    if name.endswith('.lay'):
        layout = try_to_load('layouts/' + name)
        if layout is None:
            layout = try_to_load(name)
    else:
        layout = try_to_load('layouts/' + name + '.lay')
        if layout is None:
            layout = try_to_load(name + '.lay')
    if layout is None and back >= 0:
        curdir = os.path.abspath('.')
        os.chdir('..')
        layout = get_layout(name, back - 1)
        os.chdir(curdir)
    return layout


def try_to_load(fullname):
    """Trying to load the file"""
    if not os.path.exists(fullname):
        return None
    with open(fullname,encoding="utf8") as file:
        try:
            return Layout([line.strip() for line in file])
        finally:
            file.close()
