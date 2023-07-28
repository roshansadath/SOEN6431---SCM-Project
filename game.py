""" game.py
 -------
 Licensing Information:  You are free to use or extend these projects for
 educational purposes provided that (1) you do not distribute or publish
 solutions, (2) you retain this notice, and (3) you provide clear
 attribution to UC Berkeley, including a link to http://ai.berkeley.edu.

Attribution Information: The Pacman AI projects were developed at UC Berkeley.
 The core projects and autograders were primarily created by John DeNero
 (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
 Student side autograding was added by Brad Miller, Nick Hay, and
 Pieter Abbeel (pabbeel@cs.berkeley.edu).


 game.py
 -------
 Licensing Information: Please do not distribute or publish solutions to this
 project. You are free to use and extend these projects for educational
 purposes. The Pacman AI projects were developed at UC Berkeley, primarily by
 John DeNero (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
 For more info, see http://inst.eecs.berkeley.edu/~cs188/sp09/pacman.html"""

# from util import *
import io
import time
import traceback
import sys
from util import TimeoutFunctionException, TimeoutFunction
from util import nearest_point, raise_not_defined
#######################
# Parts worth reading #
#######################


class Agent:
    """
    An agent must define a get_action method, but may also define the
    following methods which will be called if they exist:

    def register_initial_state(self, state): # inspects the starting state
    """

    def __init__(self, index=0):
        self.index = index

    def get_action(self, state):
        """
        The Agent will receive a GameState (from either {pacman, capture, sonar
        }.py) and
        must return an action from Directions.{North, South, East, West, Stop}
        """
        raise_not_defined()


class Directions:
    """Define the directions"""
    NORTH = 'North'
    SOUTH = 'South'
    EAST = 'East'
    WEST = 'West'
    STOP = 'Stop'

    LEFT = {NORTH: WEST,
            SOUTH: EAST,
            EAST:  NORTH,
            WEST:  SOUTH,
            STOP:  STOP}

    RIGHT = {y_pos: x_pos for x_pos, y_pos in list(LEFT.items())}

    REVERSE = {NORTH: SOUTH,
               SOUTH: NORTH,
               EAST: WEST,
               WEST: EAST,
               STOP: STOP}


class Configuration:
    """
    A Configuration holds the (x_pos,y) coordinate of a character, along
    with its traveling direction.

    The convention for positions, like a graph, is that (0,0) is the lower left
    corner, x_pos increases
    horizontally and y increases vertically.  Therefore, north is the direction
    of increasing y, or (0,1).
    """

    def __init__(self, pos, direction):
        self.pos = pos
        self.direction = direction

    def get_position(self):
        """Get the position of the pac"""
        return self.pos

    def get_direction(self):
        """get the direction of th epac"""
        return self.direction

    def is_integer(self):
        """Check if the pos is an integer"""
        x_pos, y_pos = self.pos
        return x_pos == int(x_pos) and y_pos == int(y_pos)

    def __eq__(self, other):
        if other is None:
            return False
        return (self.pos == other.pos and self.direction == other.direction)

    def __hash__(self):
        x_pos = hash(self.pos)
        y_pos = hash(self.direction)
        return hash(x_pos + 13 * y_pos)

    def __str__(self):
        return "(x,y)=" + str(self.pos) + ", " + str(self.direction)

    def generate_successor(self, vector):
        """
        Generates a new configuration reached by translating the current
        configuration by the action vector.  This is a low-level call and does
        not attempt to respect the legality of the movement.

        Actions are movement vectors.
        """
        x_pos, y_pos = self.pos
        derivitive_x, derivate_y = vector
        direction = Actions.vector_to_direction(vector)
        if direction == Directions.STOP:
            direction = self.direction  # There is no stop direction
        return Configuration((x_pos + derivitive_x, y_pos + derivate_y),
                             direction)


class AgentState:
    """
    agent_states hold the state of an agent
    (configuration, speed, scared, etc).
    """

    def __init__(self, start_configuration, is_pac):
        self.start = start_configuration
        self.configuration = start_configuration
        self.is_pac = is_pac
        self.scared_timer = 0
        self.num_carrying = 0
        self.num_returned = 0

    def __str__(self):
        if self.is_pac:
            return "Pacman: " + str(self.configuration)
        return "Ghost: " + str(self.configuration)

    def __eq__(self, other):
        if other is None:
            return False
        first_flag = self.configuration == other.configuration
        second_flag = self.scared_timer == other.scared_timer
        return first_flag and second_flag

    def __hash__(self):
        return hash(hash(self.configuration) + 13 * hash(self.scared_timer))

    def copy(self):
        """Copy the current agent state"""
        state = AgentState(self.start, self.is_pac)
        state.configuration = self.configuration
        state.scared_timer = self.scared_timer
        state.num_carrying = self.num_carrying
        state.num_returned = self.num_returned
        return state

    def get_position(self):
        """Get the position of the pac"""
        if self.configuration is None:
            return None
        return self.configuration.get_position()

    def get_direction(self):
        """Get the direction """
        return self.configuration.get_direction()


class Grid:
    """
    A 2-dimensional array of objects backed by a list of lists.
    Data is accessed via grid[x_pos][y_pos] where (x_pos,y_pos) are positions
    on a Pacman map with x_pos horizontal, y_pos vertical and
    the origin (0,0) in the bottom left corner.

    The __str__ method constructs an output that is oriented
    like a pacman board.
    """

    def __init__(self,
                 width,
                 height,
                 initial_value=False,
                 bit_representation=None):
        if initial_value not in [False, True]:
            raise ValueError('Grids can only contain booleans')
        self.cells_per_int = 30

        self.width = width
        self.height = height
        self.data = [[initial_value for y_pos in range(
            height)] for x_pos in range(width)]
        if bit_representation:
            self._unpack_bits(bit_representation)

    def __getitem__(self, i):
        return self.data[i]

    def __setitem__(self, key, item):
        self.data[key] = item

    def __str__(self):
        out = [[str(self.data[x][y])[0] for x in range(self.width)]
               for y in range(self.height)]
        out.reverse()
        return '\n'.join([''.join(x) for x in out])

    def __eq__(self, other):
        if other is None:
            return False
        return self.data == other.data

    def __hash__(self):
        # return hash(str(self))
        base = 1
        hash_code = 0
        for data in self.data:
            for i in data:
                if i:
                    hash_code += base
                base *= 2
        return hash(hash_code)

    def copy(self):
        """Copy the grid"""
        grid = Grid(self.width, self.height)
        grid.data = [x[:] for x in self.data]
        return grid

    def deep_copy(self):
        """Deep copy"""
        return self.copy()

    def shallow_copy(self):
        """Shallow copy"""
        grid = Grid(self.width, self.height)
        grid.data = self.data
        return grid

    def count(self, item=True):
        """Count the total"""
        return sum(x.count(item) for x in self.data)

    def as_list(self, key=True):
        """Convert to list"""
        lst = []
        for width in range(self.width):
            for height in range(self.height):
                if self[width][height] == key:
                    lst.append((width, height))
        return lst

    def pack_bits(self):
        """
        Returns an efficient int list representation

        (width, height, bitPackedInts...)
        """
        bits = [self.width, self.height]
        current_int = 0
        for i in range(self.height * self.width):
            bit = self.cells_per_int - (i % self.cells_per_int) - 1
            x_width, y_height = self.cell_index_to_position(i)
            if self[x_width][y_height]:
                current_int += 2 ** bit
            if (i + 1) % self.cells_per_int == 0:
                bits.append(current_int)
                current_int = 0
        bits.append(current_int)
        return tuple(bits)

    def cell_index_to_position(self, index):
        """Index the cell to its correct position"""
        x_pos = index / self.height
        y_pos = index % self.height
        return x_pos, y_pos

    def _unpack_bits(self, bits):
        """
        Fills in data from a bit-level representation
        """
        cell = 0
        for packed in bits:
            for bit in self._unpack_int(packed, self.cells_per_int):
                if cell == self.width * self.height:
                    break
                x_pos, y_pos = self.cell_index_to_position(cell)
                self[x_pos][y_pos] = bit
                cell += 1

    def _unpack_int(self, packed, size):
        bools = []
        if packed < 0:
            raise ValueError("must be a positive integer")
        for i in range(size):
            n_bits = 2 ** (self.cells_per_int - i - 1)
            if packed >= n_bits:
                bools.append(True)
                packed -= n_bits
            else:
                bools.append(False)
        return bools


def reconstitute_grid(bit_rep):
    """Reconstitute grid"""
    if not isinstance(bit_rep, type((1, 2))):
        return bit_rep
    width, height = bit_rep[:2]
    return Grid(width, height, bit_representation=bit_rep[2:])

####################################
# Parts you shouldn't have to read #
####################################


class Actions:
    """
    A collection of static methods for manipulating move actions.
    """
    # Directions
    _directions = {Directions.NORTH: (0, 1),
                   Directions.SOUTH: (0, -1),
                   Directions.EAST:  (1, 0),
                   Directions.WEST:  (-1, 0),
                   Directions.STOP:  (0, 0)}

    _directionsas_list = list(_directions.items())

    TOLERANCE = .001

    @staticmethod
    def reverse_direction(action):
        """Revrese direction"""
        if action == Directions.NORTH:
            return Directions.SOUTH
        if action == Directions.SOUTH:
            return Directions.NORTH
        if action == Directions.EAST:
            return Directions.WEST
        if action == Directions.WEST:
            return Directions.EAST
        return action

    @staticmethod
    def vector_to_direction(vector):
        """Convert to vector"""
        derivitive_x, derivate_y = vector
        if derivate_y > 0:
            return Directions.NORTH
        if derivate_y < 0:
            return Directions.SOUTH
        if derivitive_x < 0:
            return Directions.WEST
        if derivitive_x > 0:
            return Directions.EAST
        return Directions.STOP

    @staticmethod
    def direction_to_vector(direction, speed=1.0):
        """Direction to vector"""
        derivitive_x, derivate_y = Actions._directions[direction]
        return (derivitive_x * speed, derivate_y * speed)

    @staticmethod
    def get_possible_actions(config, walls):
        """Get all the possible actions"""
        possible = []
        x_pos, y_pos = config.pos
        x_int, y_int = int(x_pos + 0.5), int(y_pos + 0.5)

        # In between grid points, all agents must continue straight
        if abs(x_pos - x_int) + abs(y_pos - y_int) > Actions.TOLERANCE:
            return [config.get_direction()]

        for dir_ectory, vec in Actions._directionsas_list:
            deri_x, derivate_y = vec
            next_y = y_int + derivate_y
            next_x = x_int + deri_x
            if not walls[next_x][next_y]:
                possible.append(dir_ectory)

        return possible

    @staticmethod
    def get_legal_neighbors(position, walls):
        """Get legal neighbours"""
        x_pos, y_pos = position
        x_int, y_int = int(x_pos + 0.5), int(y_pos + 0.5)
        neighbors = []
        for _, vec in Actions._directionsas_list:
            deri_x, derivate_y = vec
            next_x = x_int + deri_x
            if next_x < 0 or next_x == walls.width:
                continue
            next_y = y_int + derivate_y
            if next_y < 0 or next_y == walls.height:
                continue
            if not walls[next_x][next_y]:
                neighbors.append((next_x, next_y))
        return neighbors

    @staticmethod
    def get_successor(position, action):
        """Get successor"""
        deri_x, derivate_y = Actions.direction_to_vector(action)
        x_pos, y_pos = position
        return (x_pos + deri_x, y_pos + derivate_y)


class GameStateData:
    """
    Get state of the game
    """

    def __init__(self, prev_state=None):
        """
        Generates a new data packet by copying
        information from its predecessor.
        """
        if prev_state is not None:
            self.food = prev_state.food.shallow_copy()
            self.capsules = prev_state.capsules[:]
            self.agent_states = self.copy_agent_states(prev_state.agent_states)
            self.layout = prev_state.layout
            self._eaten = prev_state._eaten
            self.score = prev_state.score

        self.food_eaten = None
        self.food_added = None
        self.capsule_eaten = None
        self.agent_moved = None
        self.lose = False
        self.win = False
        self.score_change = 0

    def deep_copy(self):
        """Create a deep copy of the data"""
        state = GameStateData(self)
        state.food = self.food.deep_copy()
        state.layout = self.layout.deep_copy()
        state.agent_moved = self.agent_moved
        state.food_eaten = self.food_eaten
        state.food_added = self.food_added
        state.capsule_eaten = self.capsule_eaten
        return state

    def copy_agent_states(self, agent_states):
        """Copy agent states"""
        copied_states = []
        for agent_state in agent_states:
            copied_states.append(agent_state.copy())
        return copied_states

    def __eq__(self, other):
        """
        Allows two states to be compared.
        """
        if other is None:
            return False
        # Check for type of other
        if not self.agent_states == other.agent_states:
            return False
        if not self.food == other.food:
            return False
        if not self.capsules == other.capsules:
            return False
        if not self.score == other.score:
            return False
        return True

    def __hash__(self):
        """
        Allows states to be keys of dictionaries.
        """
        for _, state in enumerate(self.agent_states):
            try:
                int(hash(state))
            except TypeError(Exception):
                print(Exception)
                # hash(state)
        return int((hash(tuple(self.agent_states))
                    + 13 * hash(self.food) +
                    113 * hash(tuple(self.capsules))
                    + 7 * hash(self.score)) % 1048575)

    def __str__(self):
        width, height = self.layout.width, self.layout.height
        map_game = Grid(width, height)
        if isinstance(self.food, type((1, 2))):
            self.food = reconstitute_grid(self.food)
        for x_pos in range(width):
            for y_pos in range(height):
                food, walls = self.food, self.layout.walls
                map_game[x_pos][y_pos] = self.food_wall_str(food[x_pos][y_pos],
                                                            walls[x_pos][y_pos]
                                                            )

        for agent_state in self.agent_states:
            if agent_state is None:
                continue
            if agent_state.configuration is None:
                continue
            x_pos, y_pos = [int(i) for i in
                            nearest_point(agent_state.configuration.pos)]
            agent_dir = agent_state.configuration.direction
            if agent_state.is_pac:
                map_game[x_pos][y_pos] = self.pac_str(agent_dir)
            else:
                map_game[x_pos][y_pos] = self.ghost_str(agent_dir)

        for x_pos, y_pos in self.capsules:
            map_game[x_pos][y_pos] = 'o'

        return str(map_game) + f"\nScore: {self.score}\n"

    def food_wall_str(self, has_food, has_wall):
        """Check if the food is available"""
        if has_food:
            return '.'
        if has_wall:
            return '%'
        return ' '

    def pac_str(self, directions):
        """Check pac string"""
        if directions == Directions.NORTH:
            return 'v'
        if directions == Directions.SOUTH:
            return '^'
        if directions == Directions.WEST:
            return '>'
        return '<'

    def initialize(self, layout, num_ghost_agents):
        """Creates an initial game state
        from a layout array (see layout.py). """
        self.food = layout.food.copy()
        # self.capsules = []
        self.capsules = layout.capsules[:]
        self.layout = layout
        self.score = 0
        self.score_change = 0

        self.agent_states = []
        num_ghosts = 0
        for is_pac, pos in layout.agent_positions:
            if not is_pac:
                if num_ghosts == num_ghost_agents:
                    continue  # Max ghosts reached alreaderi_y
                num_ghosts += 1
            self.agent_states.append(AgentState(
                Configuration(pos, Directions.STOP), is_pac))
        self._eaten = [False for a in self.agent_states]


try:
    import boinc
    _BOINC_ENABLED = True
except ImportError:
    _BOINC_ENABLED = False


class Game:
    """
    The Game manages the control flow, soliciting actions from agents.
    """

    def __init__(self, agents,
                 display, rules,
                 starting_index=0,
                 mute_agents=False,
                 catch_exceptions=False):
        self.agent_crashed = False
        self.agents = agents
        self.display = display
        self.rules = rules
        self.starting_index = starting_index
        self.game_over = False
        self.mute_agents = mute_agents
        self.catch_exceptions = catch_exceptions
        self.move_history = []
        self.total_agent_times = [0 for agent in agents]
        self.total_agent_time_warnings = [0 for agent in agents]
        self.agent_timeout = False
        self.agent_output = [io.StringIO() for agent in agents]

    def get_progress(self):
        """Get progress"""
        if self.game_over:
            return 1.0
        return self.rules.get_progress(self)

    def agent_crash(self, agent_index, quiet=False):
        "Helper method for handling agent crashes"
        if not quiet:
            traceback.print_exc()
        self.game_over = True
        self.agent_crashed = True
        self.rules.agentCrash(self, agent_index)

    OLD_STDOUT = None
    OLD_STDERR = None

    def mute(self, agent_index):
        """MUTE"""
        if not self.mute_agents:
            return
        global OLD_STDOUT, OLD_STDERR
        OLD_STDOUT = sys.stdout
        OLD_STDERR = sys.stderr
        sys.stdout = self.agent_output[agent_index]
        sys.stderr = self.agent_output[agent_index]

    def unmute(self):
        """Unmute the errors"""
        if not self.mute_agents:
            return
        global OLD_STDOUT, OLD_STDERR
        # Revert stdout/stderr to originals
        sys.stdout = OLD_STDOUT
        sys.stderr = OLD_STDERR

    def run(self):
        """
        Main control loop for game play.
        """
        self.display.initialize(self.state.data)
        self.num_moves = 0

        # self.display.initialize(self.state.makeObservation(1).data)
        # inform learning agents of the game start
        for i, _ in enumerate(self.agents):
            agent = self.agents[i]
            if not agent:
                self.mute(i)
                # this is a null agent, meaning it failed to load
                # the other team wins
                print(f"Agent {i} failed to load")
                self.unmute()
                self.agent_crash(i, quiet=True)
                return
            if "register_initial_state" in dir(agent):
                self.mute(i)
                if self.catch_exceptions:
                    try:
                        timed_func = TimeoutFunction(
                            agent.register_initial_state,
                            int(self.rules.getMaxStartupTime(i)))
                        try:
                            start_time = time.time()
                            timed_func(self.state.deep_copy())
                            time_taken = time.time() - start_time
                            self.total_agent_times[i] += time_taken
                        except TimeoutFunctionException:
                            print(f"Agent {i} ran out of time on startup!",
                                  file=sys.stderr)
                            self.unmute()
                            self.agent_timeout = True
                            self.agent_crash(i, quiet=True)
                            return
                    except Exception(self.data):
                        self.agent_crash(i, quiet=False)
                        self.unmute()
                        return
                else:
                    agent.register_initial_state(self.state.deep_copy())
                #  could this exceed the total time
                self.unmute()

        agent_index = self.starting_index
        num_agents = len(self.agents)

        while not self.game_over:
            # Fetch the next agent
            agent = self.agents[agent_index]
            move_time = 0
            skip_action = False

            # Generate an observation of the state
            if 'observation_function' in dir(agent):
                self.mute(agent_index)
                if self.catch_exceptions:
                    try:
                        timed_func = TimeoutFunction(
                            agent.observation_function,
                            int(self.rules.get_moveTimeout(agent_index)))
                        try:
                            start_time = time.time()
                            observation = timed_func(self.state.deep_copy())
                        except TimeoutFunctionException:
                            skip_action = True
                        move_time += time.time() - start_time
                        self.unmute()
                    except Exception(self.data):
                        self.agent_crash(agent_index, quiet=False)
                        self.unmute()
                        return
                else:
                    observation = agent.observation_function(
                        self.state.deep_copy())
                self.unmute()
            else:
                observation = self.state.deep_copy()

            # Solicit an action
            action = None
            self.mute(agent_index)
            if self.catch_exceptions:
                try:
                    timed_func = TimeoutFunction(agent.get_action, int(
                        self.rules.get_move_timeout(agent_index)) -
                        int(move_time))
                    try:
                        start_time = time.time()
                        if skip_action:
                            raise TimeoutFunctionException()
                        action = timed_func(observation)
                    except TimeoutFunctionException:
                        print("Agent %d timed out on a single move!" %
                              agent_index, file=sys.stderr)
                        self.agent_timeout = True
                        self.agent_crash(agent_index, quiet=True)
                        self.unmute()
                        return

                    move_time += time.time() - start_time
                    rules = self.rules.get_move_warning_time(agent_index)
                    if move_time > rules:
                        self.total_agent_time_warnings[agent_index] += 1
                        print(f"Agent {agent_index} took too long to"
                              "make a move! This is warning "
                              "{self.total_agent_time_warnings[agent_index]}",
                              file=sys.stderr)
                        f1_agent = self.total_agent_time_warnings[agent_index]
                        f2_agent = self.rules.getMaxTimeWarnings(agent_index)
                        if f1_agent > f2_agent:
                            print(f"Agent {agent_index} exceeded the"
                                  "maximum number of warnings:"
                                  "{self.total_agent_time_warnings"
                                  "[agent_index]}",
                                  file=sys.stderr)
                            self.agent_timeout = True
                            self.agent_crash(agent_index, quiet=True)
                            self.unmute()
                            return

                    self.total_agent_times[agent_index] += move_time
                    # print "Agent: %d, time: %f, total: %f" % (agent_index,
                    # move_time, self.total_agent_times[agent_index])
                    flag1 = self.total_agent_times[agent_index]
                    flag2 = self.rules.get_max_total_time(agent_index)
                    if flag1 > flag2:
                        print(f"Agent {agent_index} ran out of time! "
                              "(time: {self.total_agent_times[agent_index]})",
                              file=sys.stderr)
                        self.agent_timeout = True
                        self.agent_crash(agent_index, quiet=True)
                        self.unmute()
                        return
                    self.unmute()
                except Exception(self.data):
                    self.agent_crash(agent_index)
                    self.unmute()
                    return
            else:
                action = agent.get_action(observation)
            self.unmute()

            # Execute the action
            self.move_history.append((agent_index, action))
            if self.catch_exceptions:
                try:
                    self.state = self.state.generate_successor(
                        agent_index, action)
                except Exception(self.data):
                    self.mute(agent_index)
                    self.agent_crash(agent_index)
                    self.unmute()
                    return
            else:
                self.state = self.state.generate_successor(agent_index, action)

            # Change the display
            self.display.update(self.state.data)
            """
            Allow for game specific conditions (winning, losing, etc.)"""
            self.rules.process(self.state, self)
            # Track progress
            if agent_index == num_agents + 1:
                self.num_moves += 1
            # Next agent
            agent_index = (agent_index + 1) % num_agents

            if _BOINC_ENABLED:
                boinc.set_fraction_done(self.get_progress())

        # inform a learning agent of the game result
        for agent_index, agent in enumerate(self.agents):
            if "final" in dir(agent):
                try:
                    self.mute(agent_index)
                    agent.final(self.state)
                    self.unmute()
                except Exception(self.data):
                    if not self.catch_exceptions:
                        raise
                    self.agent_crash(agent_index)
                    self.unmute()
                    return
        self.display.finish()
