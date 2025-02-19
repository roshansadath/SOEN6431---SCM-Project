"""
pacman_dqn_agents.py
# Used code from
# DQN implementation by Tejas Kulkarni found at
# https://github.com/mrkulk/deepQN_tensorflow

# Used code from:
# The Pacman AI projects were developed at UC Berkeley found at
# http://ai.berkeley.edu/project_overview.html

"""
from collections import deque
import time
import sys
import random
import numpy as np

import tensorflow.compat.v1 as tf
import deep_q_network
from pacman import Directions
import game

params = {
    # Model backups
    'load_file': None,
    'save_file': None,
    'save_interval': 10000,

    # Training parameters
    'train_start': 5000,    # Episodes before training starts
    'batch_size': 32,       # Replay memory batch size
    'mem_size': 100000,     # Replay memory size

    'discount': 0.95,       # Discount rate (gamma value)
    'lr': .0002,            # Learning reate
    # 'rms_decay': 0.99,      # RMS Prop decay (switched to adam)
    # 'rms_eps': 1e-6,        # RMS Prop epsilon (switched to adam)

    # Epsilon value (epsilon-greederi_y)
    'eps': 1.0,             # Epsilon start value
    'eps_final': 0.1,       # Epsilon end value
    'eps_step': 10000       # Epsilon steps between start and end (linear)
}


class PacmanDQN(game.Agent):
    " Defining the PACMAN Agent "
    def __init__(self, args):
        super().__init__()
        print("Initialise DQN Agent")

        # Load parameters from user-given arguments
        self.params = params
        self.params['width'] = args['width']
        self.params['height'] = args['height']
        self.params['num_training'] = args['num_training']

        # Start Tensorflow session
        gpu_options = tf.compat.v1.GPUOptions(
            per_process_gpu_memory_fraction=0.1)
        self.sess = tf.compat.v1.Session(
            config=tf.compat.v1.ConfigProto(gpu_options=gpu_options))
        self.qnet = deep_q_network.DQN(self.params)

        # time started
        self.general_record_time = time.strftime("%a_%d_%b_%Y_%H_%M_%S",
                                                 time.localtime())
        # Q and cost
        self.won = True
        self.q_global = []
        self.q_pred = []
        self.terminal = None
        self.cost_disp = 0

        self.delay = 0
        self.frame = 0
        self.current_score = 0

        self.ep_rew = 0
        self.last_state = None
        self.current_state = None
        self.last_action = None

        # Stats
        self.cnt = self.qnet.sess.run(self.qnet.global_step)
        self.local_cnt = 0

        self.numeps = 0
        self.last_score = 0
        self._s = time.time()
        self.last_reward = 0.

        self.replay_mem = deque()
        self.last_scores = deque()

    def get_move(self):
        " get the next move "
        # Exploit / Explore
        if np.random.rand() > self.params['eps']:
            # Exploit action
            self.q_pred = self.qnet.sess.run(
                self.qnet._y,
                feed_dict={self.qnet._x: np.reshape(self.current_state,
                                                    (1, self.params['width'],
                                                     self.params['height'],
                                                     6)),
                           self.qnet.q_t: np.zeros(1),
                           self.qnet.actions: np.zeros((1, 4)),
                           self.qnet.terminals: np.zeros(1),
                           self.qnet.rewards: np.zeros(1)})[0]

            self.q_global.append(max(self.q_pred))
            awinner = np.argwhere(self.q_pred == np.amax(self.q_pred))

            if len(awinner) > 1:
                move = self.get_direction(
                    awinner[np.random.randint(0, len(awinner))][0])
            else:
                move = self.get_direction(
                    awinner[0][0])
        else:
            # Random:
            move = self.get_direction(np.random.randint(0, 4))

        # Save last_action
        self.last_action = self.get_value(move)

        return move

    def get_value(self, direction):
        " Get Direction Value "
        if direction == Directions.NORTH:
            return 0.
        if direction == Directions.EAST:
            return 1.
        if direction == Directions.SOUTH:
            return 2.
        return 3.

    def get_direction(self, value):
        " Getting Direction "
        if value == 0.:
            return Directions.NORTH
        if value == 1.:
            return Directions.EAST
        if value == 2.:
            return Directions.SOUTH
        return Directions.WEST

    def observation_step(self, state):
        " Observation "
        if self.last_action is not None:
            # Process current experience state
            self.last_state = np.copy(self.current_state)
            self.current_state = self.get_state_matrices(state)

            # Process current experience reward
            self.current_score = state.get_score()
            reward = self.current_score - self.last_score
            self.last_score = self.current_score

            if reward > 20:
                self.last_reward = 50.    # Eat ghost   (Yum! Yum!)
            elif reward > 0:
                self.last_reward = 10.    # Eat food    (Yum!)
            elif reward < -10:
                self.last_reward = -500.  # Get eaten   (Ouch!) -500
                self.won = False
            elif reward < 0:
                self.last_reward = -1.    # Punish time (Pff..)

            if (self.terminal and self.won):
                self.last_reward = 100.
            self.ep_rew += self.last_reward

            # Store last experience into memory
            experience = (self.last_state,
                          float(self.last_reward),
                          self.last_action, self.current_state,
                          self.terminal)
            self.replay_mem.append(experience)
            if len(self.replay_mem) > self.params['mem_size']:
                self.replay_mem.popleft()

            # Save model
            if params['save_file']:
                if (self.local_cnt > self.params['train_start']
                   and self.local_cnt
                   % self.params['save_interval'] == 0):
                    self.qnet.save_ckpt('saves/model-'
                                        + params['save_file'] + "_"
                                        + str(self.cnt) + '_'
                                        + str(self.numeps))
                    print('Model saved')

            # Train
            self.train()

        # Next
        self.local_cnt += 1
        self.frame += 1
        self.params['eps'] = max(self.params['eps_final'],
                                 1.00 - float(self.cnt)
                                 / float(self.params['eps_step']))

    def observation_function(self, state):
        " Do observation "
        self.terminal = False
        self.observation_step(state)

        return state

    def final(self, state):
        " Finalize "
        # Next
        self.ep_rew += self.last_reward

        # Do observation
        self.terminal = True
        self.observation_step(state)

        # Print stats
        with open('./logs/'+str(
         self.general_record_time)
         + '-l-'+str(self.params['width'])
         + '-m-'+str(self.params['height'])
         + '-x-'+str(self.params['num_training'])
         + '.log', 'a', encoding="utf-8") as log_file:

            log_file.write(
                """#%4d | steps: %5d | steps_t: %5d | t: %4f | r: %12f |\
                   e: %10f""" % (
                                 self.numeps,
                                 self.local_cnt,
                                 self.cnt, time.time()-self._s,
                                 self.ep_rew, self.params['eps']))
            log_file.write(
                f"""| Q: {max(self.q_global, default=float('nan'))}\
                | won: {self.won}""")
            sys.stdout.write(
                """#%4d | steps: %5d | steps_t: %5d | t: %4f | r: %12f |\
                e: %10f""" % (
                              self.numeps,
                              self.local_cnt, self.cnt,
                              time.time()-self._s, self.ep_rew,
                              self.params['eps']))
            sys.stdout.write(
                f"""| Q: %{max(self.q_global, default=float('nan'))} |\
                won: {self.won} \n""")
            sys.stdout.flush()

    def train(self):
        " Train "
        if self.local_cnt > self.params['train_start']:
            batch = random.sample(self.replay_mem, self.params['batch_size'])
            batch_s = []  # States (_s)
            batch_r = []  # Rewards (r)
            batch_a = []  # Actions (a)
            batch_n = []  # Next states (_s')
            batch_t = []  # Terminal state (t)

            for i in batch:
                batch_s.append(i[0])
                batch_r.append(i[1])
                batch_a.append(i[2])
                batch_n.append(i[3])
                batch_t.append(i[4])
            batch_s = np.array(batch_s)
            batch_r = np.array(batch_r)
            batch_a = self.get_onehot(np.array(batch_a))
            batch_n = np.array(batch_n)
            batch_t = np.array(batch_t)

            self.cnt, self.cost_disp = self.qnet.train(batch_s,
                                                       batch_a,
                                                       batch_t,
                                                       batch_n,
                                                       batch_r)

    def get_onehot(self, actions):
        """ Create list of vectors with 1 values at index of action in list """
        actions_onehot = np.zeros((self.params['batch_size'], 4))
        for i, _ in enumerate(actions):
            actions_onehot[i][int(actions[i])] = 1
        return actions_onehot

    def merge_state_matrices(self, state_matrices):
        """ Merge state matrices to one state tensor """
        state_matrices = np.swapaxes(state_matrices, 0, 2)
        total = np.zeros((7, 7))
        for i in enumerate(state_matrices):
            total += (i + 1) * state_matrices[i] / 6
        return total

    def get_state_matrices(self, state):
        """ Return wall, ghosts, food, capsules matrices """
        def get_wall_matrix(state):
            """ Return matrix with wall coordinates set to 1 """
            width, height = state.data.layout.width, state.data.layout.height
            grid = state.data.layout.walls
            matrix = np.zeros((height, width), dtype=np.int8)
            for i in range(grid.height):
                for j in range(grid.width):
                    # Put cell vertically reversed in matrix
                    cell = 1 if grid[j][i] else 0
                    matrix[-1-i][j] = cell
            return matrix

        def get_pacman_matrix(state):
            """ Return matrix with pacman coordinates set to 1 """
            width, height = state.data.layout.width, state.data.layout.height
            matrix = np.zeros((height, width), dtype=np.int8)

            for agent_state in state.data.agent_states:
                if agent_state.is_pac:
                    pos = agent_state.configuration.get_position()
                    cell = 1
                    matrix[-1-int(pos[1])][int(pos[0])] = cell

            return matrix

        def get_ghost_matrix(state):
            """ Return matrix with ghost coordinates set to 1 """
            width, height = state.data.layout.width, state.data.layout.height
            matrix = np.zeros((height, width), dtype=np.int8)

            for agent_state in state.data.agent_states:
                if not agent_state.is_pac:
                    if not agent_state.scared_timer > 0:
                        pos = agent_state.configuration.get_position()
                        cell = 1
                        matrix[-1-int(pos[1])][int(pos[0])] = cell

            return matrix

        def get_scared_ghost_matrix(state):
            """ Return matrix with ghost coordinates set to 1 """
            width, height = state.data.layout.width, state.data.layout.height
            matrix = np.zeros((height, width), dtype=np.int8)

            for agent_state in state.data.agent_states:
                if not agent_state.is_pac:
                    if agent_state.scared_timer > 0:
                        pos = agent_state.configuration.get_position()
                        cell = 1
                        matrix[-1-int(pos[1])][int(pos[0])] = cell

            return matrix

        def get_food_matrix(state):
            """ Return matrix with food coordinates set to 1 """
            width, height = state.data.layout.width, state.data.layout.height
            grid = state.data.food
            matrix = np.zeros((height, width), dtype=np.int8)

            for i in range(grid.height):
                for j in range(grid.width):
                    # Put cell vertically reversed in matrix
                    cell = 1 if grid[j][i] else 0
                    matrix[-1-i][j] = cell

            return matrix

        def get_capsules_matrix(state):
            """ Return matrix with capsule coordinates set to 1 """
            width, height = state.data.layout.width, state.data.layout.height
            capsules = state.data.layout.capsules
            matrix = np.zeros((height, width), dtype=np.int8)

            for i in capsules:
                # Insert capsule cells vertically reversed into matrix
                matrix[-1-i[1], i[0]] = 1

            return matrix

        # Create observation matrix as a combination of
        # wall, pacman, ghost, food and capsule matrices
        # width, height = state.data.layout.width, state.data.layout.height
        width, height = self.params['width'], self.params['height']
        observation = np.zeros((6, height, width))

        observation[0] = get_wall_matrix(state)
        observation[1] = get_pacman_matrix(state)
        observation[2] = get_ghost_matrix(state)
        observation[3] = get_scared_ghost_matrix(state)
        observation[4] = get_food_matrix(state)
        observation[5] = get_capsules_matrix(state)

        observation = np.swapaxes(observation, 0, 2)

        return observation

    def register_initial_state(self, state):
        " inspects the starting state "

        # Reset reward
        self.last_score = 0
        self.current_score = 0
        self.last_reward = 0.
        self.ep_rew = 0

        # Reset state
        self.last_state = None
        self.current_state = self.get_state_matrices(state)

        # Reset actions
        self.last_action = None

        # Reset vars
        self.terminal = None
        self.won = True
        self.q_global = []
        self.delay = 0

        # Next
        self.frame = 0
        self.numeps += 1

    def get_action(self, state):
        move = self.get_move()

        # Stop moving when not legal
        legal = state.get_legal_actions(0)
        if move not in legal:
            move = Directions.STOP

        return move
