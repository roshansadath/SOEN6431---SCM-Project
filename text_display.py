"""
# text_display.py
# --------------
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

import time

try:
    import pacman
except ImportError:
    print("Import Error")

DRAW_EVERY = 1
SLEEP_TIME = 0  # This can be overwritten by __init__
DISPLAY_MOVES = False
QUIET = False  # Supresses output


class NullGraphics:
    " Define the Null Grpahics of the Game "
    def initialize(self, state, is_blue=False):
        " Initialization "

    def update(self, state):
        " Update the state "

    def check_null_display(self):
        " Null "
        return True

    def pause(self):
        " Pause Time "
        time.sleep(SLEEP_TIME)

    def draw(self, state):
        " Write the State "
        print(state)

    def update_distributions(self, dist):
        " Update The Distributions "

    def finish(self):
        " Finish "


class PacmanGraphics:
    """
    Define the Graphics for PacMan Agent
    """
    def __init__(self, speed=None):
        self.turn = 0
        self.agent_counter = 0
        global SLEEP_TIME
        if speed is not None:
            SLEEP_TIME = speed

    def initialize(self, state):
        " Initialization "
        self.draw(state)
        self.pause()

    def update(self, state):
        " Update State "
        num_agents = len(state.agent_states)
        self.agent_counter = (self.agent_counter + 1) % num_agents
        if self.agent_counter == 0:
            self.turn += 1
            if DISPLAY_MOVES:
                ghosts = [pacman.nearest_point(state.getGhostPosition(i))
                          for i in range(1, num_agents)]
                print((f"""{self.turn}) P:{str(pacman.nearest_point(
                    state.getPacmanPosition()))}""",
                       f'| Score: {state.score}',
                       '| Ghosts:',
                       ghosts))
            if self.turn % DRAW_EVERY == 0:
                self.draw(state)
                self.pause()
        if state.win or state.lose:
            self.draw(state)

    def pause(self):
        " Pause Time "
        time.sleep(SLEEP_TIME)

    def draw(self, state):
        " Write state "
        print(state)

    def finish(self):
        " Finish mode "
