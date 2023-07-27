"""

# pacman.py
# ---------
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



Pacman.py holds the logic for the classic pacman game along with the main
code to run a game.  This file is divided into three sections:

  (i)  Your interface to the pacman world:
          Pacman is a complex environment.  You probably don't want to
          read through all of the code we wrote to make the game runs
          correctly.  This section contains the parts of the code
          that you will need to understand in order to complete the
          project.  There is also some code in game.py that you should
          understand.

  (ii)  The hidden secrets of pacman:
          This section contains all of the logic code that the pacman
          environment uses to decide who can move where, who dies when
          things collide, etc.  You shouldn't need to read this section
          of code, but you can if you want.

  (iii) Framework to start a game:
          The final section contains the code for reading the command
          you use to set up the game, then starting up a new game, along with
          linking in all the external parts (agent functions, graphics).
          Check this section out to see all the options available to you.

To play your first game, type 'python pacman.py' from the command line.
The keys are 'a', 's', 'd', and 'w' to move (or arrow keys).  Have fun!
"""
from game import GameStateData
from game import Game
from game import Directions
from game import Actions
from util import nearest_point
from util import manhattan_distance
import layout
import sys
import time
import random
import os
import pickle
from optparse import OptionParser
import __main__
import pacman_dqn_agents
import layout

from game import GameStateData, Game, Directions, Actions
from util import nearest_point, manhattan_distance
import textDisplay as text_display
import graphics_display as graphics_display
import ghost_agents


###################################################
# YOUR INTERFACE TO THE PACMAN WORLD: A GameState #
###################################################


class GameState:
    """
    A GameState specifies the full game state, including the food, capsules,
    agent configurations and score changes.

    GameStates are used by the Game object to capture
    the actual state of the game and can be used by agents
    to reason about the game.

    Much of the information in a GameState is stored in a
    GameStateData object.  We strongly suggest that you access that data
    via the accessor methods below rather
    than referring to the GameStateData object directly.

    Note that in classic Pacman, Pacman is always agent 0.
    """

    ####################################################
    # Accessor methods: use these to access state data #
    ####################################################

    # static variable keeps track of which states have had get_legal_actions
    # called
    explored = set()

    @staticmethod
    def get_and_reset_explored():
        " Get / Reset Explorer "
        tmp = GameState.explored.copy()
        GameState.explored = set()
        return tmp

    def get_legal_actions(self, agent_index=0):
        """
        Returns the legal actions for the agent specified.
        """
        # GameState.explored.add(self)
        if self.iswin() or self.islose():
            return []

        if agent_index == 0:  # Pacman is moving
            return PacmanRules.get_legal_actions(self)
        return GhostRules.get_legal_actions(self, agent_index)

    def generate_successor(self, agent_index, action):
        """
        Returns the successor state after the specified agent takes the action.
        """
        # Check that successors exist
        if self.iswin() or self.islose():
            raise UserWarning("Can't generate a successor of terminal state")

        # Copy current state
        state = GameState(self)

        # Let agent's logic deal with its action's effects on the board
        if agent_index == 0:  # Pacman is moving
            state.data._eaten = [False for _ in range(state.get_num_agents())]
            PacmanRules.apply_action(state, action)
        else:                # A ghost is moving
            GhostRules.apply_action(state, action, agent_index)

        # Time passes
        if agent_index == 0:
            # Penalty for waiting around
            state.data.score_change += -TIME_PENALTY
        else:
            GhostRules.decrement_timer(state.data.agent_states[agent_index])

        # Resolve multi-agent effects
        GhostRules.check_death(state, agent_index)

        # Book keeping
        state.data.agent_moved = agent_index
        state.data.score += state.data.score_change
        GameState.explored.add(self)
        GameState.explored.add(state)
        return state

    def get_legal_pacman_actions(self):
        " Get Legal Actions for Pacman "
        return self.get_legal_actions(0)

    def generate_pacman_successor(self, action):
        """
        Generates the successor state after the specified pacman move
        """
        return self.generate_successor(0, action)

    def get_pacman_state(self):
        """
        Returns an AgentState object for pacman (in game.py)

        state.pos gives the current position
        state.direction gives the travel vector
        """
        return self.data.agent_states[0].copy()

    def get_pacman_position(self):
        " Get Pacman's Position "
        return self.data.agent_states[0].get_position()

    def get_ghost_states(self):
        " Get the Ghost's States "
        return self.data.agent_states[1:]

    def get_ghost_state(self, agent_index):
        " Get the State of a particular Ghost "
        if agent_index == 0 or agent_index >= self.get_num_agents():
            raise UserWarning("Invalid index passed to get_ghost_state")
        return self.data.agent_states[agent_index]

    def get_ghost_position(self, agent_index):
        " Get the Ghost's Location "
        if agent_index == 0:
            raise UserWarning("Pacman's index passed to get_ghost_position")
        return self.data.agent_states[agent_index].get_position()

    def get_ghost_positions(self):
        " Get Postions of Ghosts "
        return [s.get_position() for s in self.get_ghost_states()]

    def get_num_agents(self):
        " Get Numebr of Agents "
        return len(self.data.agent_states)

    def get_score(self):
        " Get Total Score "
        return float(self.data.score)

    def get_capsules(self):
        """
        Returns a list of positions (x,y) of the remaining capsules.
        """
        return self.data.capsules

    def get_num_food(self):
        " Get Number of Foods "
        return self.data.food.count()

    def get_food(self):
        """
        Returns a Grid of boolean food indicator variables.

        Grids can be accessed via list notation, so to check
        if there is food at (x,y), just call

        currentFood = state.get_food()
        if currentFood[x][y] == True: ...
        """
        return self.data.food

    def get_walls(self):
        """
        Returns a Grid of boolean wall indicator variables.

        Grids can be accessed via list notation, so to check
        if there is a wall at (x,y), just call

        walls = state.get_walls()
        if walls[x][y] == True: ...
        """
        return self.data.layout.walls

    def has_food(self, _x, _y):
        " Check if the postionn has food "
        return self.data.food[_x][_y]

    def has_wall(self, _x, _y):
        " Check if the postion has wall "
        return self.data.layout.walls[_x][_y]

    def islose(self):
        " Check if it is a losing position "
        return self.data.lose

    def iswin(self):
        return self.data.win

    #############################################
    #             Helper methods:               #
    # You shouldn't need to call these directly #
    #############################################

    def __init__(self, prev_state=None):
        """
        Generates a new state by copying information from its predecessor.
        """
        self.quiet = False
        if prev_state is not None:  # Initial state
            self.data = GameStateData(prev_state.data)
        else:
            self.data = GameStateData()

    def deep_copy(self):
        "Create a Deep Copy"
        state = GameState(self)
        state.data = self.data.deep_copy()
        return state

    def __eq__(self, other):
        """
        Allows two states to be compared.
        """
        return hasattr(other, 'data') and self.data == other.data

    def __hash__(self):
        """
        Allows states to be keys of dictionaries.
        """
        return hash(self.data)

    def __str__(self):
        " Define a string"
        return str(self.data)

    def initialize(self, layout, num_ghost_agents=1000):
        """
        Creates an initial game state from a layout array (see layout.py).
        """
        self.data.initialize(layout, num_ghost_agents)


############################################################################
#                     THE HIDDEN SECRETS OF PACMAN                         #
#                                                                          #
# You shouldn't need to look through the code in this section of the file. #
############################################################################

SCARED_TIME = 40    # Moves ghosts are scared
COLLISION_TOLERANCE = 0.7  # How close ghosts must be to Pacman to kill
TIME_PENALTY = 1  # Number of points lost each round


class ClassicGameRules:
    """
    These game rules manage the control flow of a game, deciding when
    and how the game starts and ends.
    """

    def __init__(self, timeout=30):
        self.timeout = timeout

    def new_game(self, layout, pacmanAgent, ghostAgents,
                 display, quiet=False, catch_exceptions=False):
        " Start New Game Parameters "
        agents = [pacmanAgent] + ghostAgents[:layout.get_num_ghosts()]
        init_state = GameState()
        init_state.initialize(layout, len(ghostAgents))
        game = Game(agents, display, self, catch_exceptions=catch_exceptions)
        game.state = init_state
        self.initial_state = init_state.deep_copy()
        self.quiet = quiet
        return game

    def process(self, state, game):
        """
        Checks to see whether it is time to end the game.
        """
        if state.iswin():
            self.win(state, game)
        if state.islose():
            self.lose(state, game)

    def win(self, state, game):
        " Check if it is a winning position "
        if not self.quiet:
            print(f"Pacman emerges victorious ! \nScore: {state.data.score}")
        game.game_over = True

    def lose(self, state, game):
        "  Losing Message "
        if not self.quiet:
            print(f"Pacman died ! \nScore: {state.data.score}")
        game.game_over = True

    def get_progress(self, game):
        " Get the Progress of the game "
        return float(game.state.get_num_food())\
            / self.initial_state.get_num_food()

    def agent_crash(self, agent_index):
        " Check if Agents have crashed "
        if agent_index == 0:
            print("Pacman crashed")
        else:
            print("A ghost crashed")

    def get_max_total_time(self):
        " Get Max Time "
        return self.timeout

    def get_max_startup_time(self):
        " Get Max Startup Time "
        return self.timeout

    def get_move_warning_time(self):
        " Get a move Warning Time "
        return self.timeout

    def get_move_timeout(self):
        " Get Move Timeout "
        return self.timeout

    def get_max_time_warnings(self):
        " Get Maximum Number of Warnings "
        return 0


class PacmanRules:
    """
    These functions govern how pacman interacts with his environment under
    the classic game rules.
    """
    PACMAN_SPEED = 1

    @staticmethod
    def get_legal_actions(state):
        """
        Returns a list of possible actions.
        """
        return Actions.get_possible_actions(
            state.get_pacman_state().configuration,
            state.data.layout.walls)

    @staticmethod
    def apply_action(state, action):
        """
        Edits the state to reflect the results of the action.
        """
        legal = PacmanRules.get_legal_actions(state)
        if action not in legal:
            raise UserWarning("Illegal action " + str(action))

        pacman_st = state.data.agent_states[0]

        # Update Configuration
        vector = Actions.direction_to_vector(action, PacmanRules.PACMAN_SPEED)
        pacman_st.configuration = pacman_st.configuration.generate_successor(
            vector)

        # Eat
        next_st = pacman_st.configuration.get_position()
        nearest = nearest_point(next_st)
        if manhattan_distance(nearest, next_st) <= 0.5:
            # Remove food
            PacmanRules.consume(nearest, state)

    @staticmethod
    def consume(position, state):
        "Eat the food"
        _x, _y = position
        # Eat food
        if state.data.food[_x][_y]:
            state.data.score_change += 10
            state.data.food = state.data.food.copy()
            state.data.food[_x][_y] = False
            state.data.food_eaten = position
            # TODO: cache num_food?
            num_food = state.get_num_food()
            if num_food == 0 and not state.data.lose:
                state.data.score_change += 500
                state.data.win = True
        # Eat capsule
        if position in state.get_capsules():
            state.data.capsules.remove(position)
            state.data.capsule_eaten = position
            # Reset all ghosts' scared timers
            for index in range(1, len(state.data.agent_states)):
                state.data.agent_states[index].scared_timer = SCARED_TIME


class LayoutNotFound(Exception):
    " Layout Error "


class GhostRules:
    """
    These functions dictate how ghosts interact with their environment.
    """
    GHOST_SPEED = 1.0

    @staticmethod
    def get_legal_actions(state, ghost_index):
        """
        Ghosts cannot stop, and cannot turn around unless they
        reach a dead end, but can turn 90 degrees at intersections.
        """
        conf = state.get_ghost_state(ghost_index).configuration
        possible_actions = Actions.get_possible_actions(
            conf, state.data.layout.walls)
        reverse = Actions.reverse_direction(conf.direction)
        if Directions.STOP in possible_actions:
            possible_actions.remove(Directions.STOP)
        if reverse in possible_actions and len(possible_actions) > 1:
            possible_actions.remove(reverse)
        return possible_actions

    @staticmethod
    def apply_action(state, action, ghost_index):
        " Apply an Action "
        legal = GhostRules.get_legal_actions(state, ghost_index)
        if action not in legal:
            raise UserWarning("Illegal ghost action " + str(action))

        ghost_state = state.data.agent_states[ghost_index]
        speed = GhostRules.GHOST_SPEED
        if ghost_state.scared_timer > 0:
            speed /= 2.0
        vector = Actions.direction_to_vector(action, speed)
        ghost_state.configuration = \
            ghost_state.configuration.generate_successor(vector)

    @staticmethod
    def decrement_timer(ghost_state):
        " Decrease the Timer "
        timer = ghost_state.scared_timer
        if timer == 1:
            ghost_state.configuration.pos = nearest_point(
                ghost_state.configuration.pos)
        ghost_state.scared_timer = max(0, timer - 1)

    @staticmethod
    def check_death(state, agent_index):
        " Check is agent is alive "
        pacman_position = state.get_pacman_position()
        if agent_index == 0:  # Pacman just moved; Anyone can kill him
            for index in range(1, len(state.data.agent_states)):
                ghost_state = state.data.agent_states[index]
                ghost_position = ghost_state.configuration.get_position()
                if GhostRules.can_kill(pacman_position, ghost_position):
                    GhostRules.collide(state, ghost_state, index)
        else:
            ghost_state = state.data.agent_states[agent_index]
            ghost_position = ghost_state.configuration.get_position()
            if GhostRules.can_kill(pacman_position, ghost_position):
                GhostRules.collide(state, ghost_state, agent_index)

    @staticmethod
    def collide(state, ghost_state, agent_index):
        " Check Collision "
        if ghost_state.scared_timer > 0:
            state.data.score_change += 200
            GhostRules.place_ghost(state, ghost_state)
            ghost_state.scared_timer = 0
            # Added for first-person
            state.data._eaten[agent_index] = True
        else:
            if not state.data.win:
                state.data.score_change -= 500
                state.data.lose = True

    @staticmethod
    def can_kill(pacman_position, ghost_position):
        " Whether the ghost can kill "
        return manhattan_distance(ghost_position,
                                  pacman_position) <= COLLISION_TOLERANCE

    @staticmethod
    def place_ghost(ghost_state):
        " Placing the Ghost "
        ghost_state.configuration = ghost_state.start

#############################
# FRAMEWORK TO START A GAME #
#############################


def default(str1):
    " Default Value "
    return str1 + ' [Default: %default]'


def parse_agent_args(str1):
    " Parse Arguments "
    if str1 is None:
        return {}
    pieces = str1.split(',')
    opts = {}
    for _p in pieces:
        if '=' in _p:
            key, val = _p.split('=')
        else:
            key, val = _p, 1
        opts[key] = val
    return opts


def read_command(argv):
    """
    Processes the command used to run pacman from the command line.
    """
    usage_str = """
    USAGE:      python pacman.py <options>
    EXAMPLES:   (1) python pacman.py
                    - starts an interactive game
                (2) python pacman.py --layout smallClassic --zoom 2
                OR  python pacman.py -l smallClassic -z 2
                    - starts an interactive game on a smaller board, zoomed in
    """
    parser = OptionParser(usage_str)

    parser.add_option('-n', '--num_games', dest='num_games', type='int',
                      help=default('the number of GAMES to play'),
                      metavar='GAMES', default=6000)
    parser.add_option('-l', '--layout', dest='layout',
                      help=default(
                          'the LAYOUT_FILE from which to load the map layout'),
                      metavar='LAYOUT_FILE', default='smallGrid')
    parser.add_option('-p', '--pacman', dest='pacman',
                      help=default(
                          'the agent TYPE in the pacmanAgents module to use'),
                      metavar='TYPE', default='PacmanDQN')
    parser.add_option('-t', '--textGraphics', action='store_true',
                      dest='textGraphics',
                      help='Display output as text only', default=False)
    parser.add_option('-q', '--quietTextGraphics', action='store_true',
                      dest='quietGraphics',
                      help="""Generate minimal output and no
                              graphics""", default=False)
    parser.add_option('-g', '--ghosts', dest='ghost',
                      help=default("""the ghost agent TYPE in the ghostAgents
                                      module to use"""),
                      metavar='TYPE',
                      default='RandomGhost')
    parser.add_option('-k',
                      '--num_ghosts', type='int', dest='num_ghosts',
                      help=default("""The maximum number of ghosts
                                   to use"""), default=4)
    parser.add_option('-z',
                      '--zoom', type='float', dest='zoom',
                      help=default("""Zoom the size of the graphics
                                   window"""), default=1.0)
    parser.add_option('-f',
                      '--fixRandomSeed',
                      action='store_true',
                      dest='fixRandomSeed',
                      help="""Fixes the random seed to
                              always play the same game""", default=False)
    parser.add_option('-r',
                      '--recordActions',
                      action='store_true',
                      dest='record',
                      help="""Writes game histories to a file (named by
                              the time they were played)""", default=False)
    parser.add_option('--replay',
                      dest='gameToReplay',
                      help="""A recorded game file (pickle) to
                              replay""", default=None)
    parser.add_option('-a',
                      '--agentArgs',
                      dest='agentArgs',
                      help="""Comma separated values sent to agent.
                              e.g. "opt1=val1,opt2,opt3=val3" """)
    parser.add_option('-x',
                      '--num_training',
                      dest='num_training',
                      type='int',
                      help=default("""How many episodes are training
                                   (suppresses output)"""), default=5000)
    parser.add_option('--frame_time',
                      dest='frame_time',
                      type='float',
                      help=default("""Time to delay between frames;
                                   <0 means keyboard"""), default=0.1)
    parser.add_option('-c',
                      '--catch_exceptions',
                      action='store_true',
                      dest='catch_exceptions',
                      help="""Turns on exception handling and timeouts
                              during games""", default=False)
    parser.add_option('--timeout',
                      dest='timeout',
                      type='int',
                      help=default("""Maximum length of time an agent can spend
                                   computing in a single game"""), default=30)

    options, otherjunk = parser.parse_args(argv)
    if len(otherjunk) != 0:
        raise UserWarning('CLI input not understood: '+str(otherjunk))
    args = {}

    # Fix the random seed
    if options.fixRandomSeed:
        random.seed('cs188')

    # Choose a layout
    args['layout'] = layout.get_layout(options.layout)
    if args['layout'] is None:
        raise LayoutNotFound("The layout " + options.layout +
                             " cannot be found")

    # Choose a Pacman agent
    no_keyboard = options.gameToReplay is None and (
        options.textGraphics or options.quietGraphics)
    pacman_type = load_agent(options.pacman, no_keyboard)
    agent_opts = parse_agent_args(options.agentArgs)

    agent_opts['width'] = layout.get_layout(options.layout).width
    agent_opts['height'] = layout.get_layout(options.layout).height

    if options.num_training > 0:
        args['num_training'] = options.num_training
        if 'num_training' not in agent_opts:
            agent_opts['num_training'] = options.num_training
    pacman = pacman_type(agent_opts)  # Instantiate Pacman with agentArgs
    args['pacman'] = pacman
    pacman.width = agent_opts['width']
    pacman.height = agent_opts['height']

    # Don't display training games
    if 'numTrain' in agent_opts:
        options.numQuiet = int(agent_opts['numTrain'])
        options.numIgnore = int(agent_opts['numTrain'])

    # Choose a ghost agent
    ghost_type = load_agent(options.ghost, no_keyboard)
    args['ghosts'] = [ghost_type(i + 1) for i in range(options.num_ghosts)]

    # Choose a display format
    if options.quietGraphics:
        args['display'] = text_display.NullGraphics()
    elif options.textGraphics:
        text_display.SLEEP_TIME = options.frame_time
        args['display'] = text_display.PacmanGraphics()
    else:
        import graphics_display
        args['display'] = graphics_display.PacmanGraphics(
            options.zoom, frame_time=options.frame_time)
    args['num_games'] = options.num_games
    args['record'] = options.record
    args['catch_exceptions'] = options.catch_exceptions
    args['timeout'] = options.timeout

    # Special case: recorded games don't use the run_games method or args
    # structure
    if options.gameToReplay is not None:
        print(f'Replaying recorded game {options.gameToReplay}.')
        with open(options.gameToReplay, encoding='utf-8') as file:
            recorded = pickle.load(file)

        recorded['display'] = args['display']
        replay_game(**recorded)
        sys.exit(0)

    return args


def load_agent(pacman, nographics):
    " Looks through all pythonPath Directories for the right module "
    python_path_str = os.path.expandvars("$PYTHONPATH")
    if python_path_str.find(';') == -1:
        python_path_dirs = python_path_str.split(':')
    else:
        python_path_dirs = python_path_str.split(';')
    python_path_dirs.append('.')

    for module_dir in python_path_dirs:
        if not os.path.isdir(module_dir):
            continue
        module_names = [f for f in os.listdir(
            module_dir) if f.endswith('gents.py')]
        for modulename in module_names:
            try:
                module = __import__(modulename[:-3])
            except ImportError:
                continue
            if pacman in dir(module):
                if nographics and modulename == 'keyboard_agents.py':
                    raise UserWarning(
                            """Using the keyboard requires
                            graphics (not text display)""")
                return getattr(module, pacman)
    raise UserWarning("The agent " + pacman +
                      " is not specified in any *Agents.py.")


def replay_game(layout, actions, display):
    " Replay Game "
    rules = ClassicGameRules()
    agents = [pacman_dqn_agents.Greederivative_yAgent()]+[
        ghost_agents.RandomGhost(i + 1) for i in range(layout.get_num_ghosts())]
    game = rules.new_game(layout, agents[0], agents[1:], display)
    state = game.state
    display.initialize(state.data)

    for action in actions:
        # Execute the action
        state = state.generate_successor(*action)
        # Change the display
        display.update(state.data)
        # Allow for game specific conditions (winning, losing, etc.)
        rules.process(state, game)

    display.finish()


def run_games(layout, pacman, ghosts,
              display, num_games, record,
              num_training=0, catch_exceptions=False,
              timeout=30):
    " Inititalize Game "
    __main__.__dict__['_display'] = display

    rules = ClassicGameRules(timeout)
    games = []

    for i in range(num_games):
        be_quiet = i < num_training
        if be_quiet:
            # Suppress output and graphics
            game_display = text_display.NullGraphics()
            rules.quiet = True
        else:
            game_display = display
            rules.quiet = False
        game = rules.new_game(layout, pacman, ghosts,
                              game_display, be_quiet, catch_exceptions)
        game.run()

        if not be_quiet:
            games.append(game)

        if record:
            fname = (f'recorded-game-{(i + 1)}') + \
                '-'.join([str(t) for t in time.localtime()[1:6]])
            with open(fname, 'w', encoding='utf-8') as file:
                components = {'layout': layout, 'actions': game.move_history}
                pickle.dump(components, file)

    if (num_games - num_training) > 0:
        scores = [game.state.get_score() for game in games]
        wins = [game.state.iswin() for game in games]
        win_rate = wins.count(True) / float(len(wins))
        print('Average Score: ', sum(scores) / float(len(scores)))
        print('Scores:   ', ', '.join([str(score) for score in scores]))
        print(f"Win Rate: {wins.count(True)}/{len(wins)} ({win_rate})")
        print('Record:       ', ', '.join(
            [['Loss', 'Win'][int(w)] for w in wins]))
        end_time = time.time()
        print(f"Execution Time = {end_time - start_time}s")

    return games


"""
    The main function called when pacman.py is run
    from the command line:

    > python pacman.py

    See the usage string for more details.

    > python pacman.py --help
"""

if __name__ == '__main__':
    start_time = time.time()
    args = read_command(sys.argv[1:])  # Get game components based on input
    run_games(**args)

    # import cProfile
    # cProfile.run("run_games( **args )")
