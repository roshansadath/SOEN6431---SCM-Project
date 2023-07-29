"""
Deep Q-Learning Model for training the PacMan
Modified version of DQN implementation by Tejas Kulkarni found at
https://github.com/mrkulk/deepQN_tensorflow

"""
import numpy as np
import tensorflow.compat.v1 as tf
tf.disable_eager_execution()


class DQN:
    """
    INITALIZING THE Deep-Q-Learning Model
    """
    def __init__(self, params):
        self.params = params
        self.network_name = 'qnet'
        self.sess = tf.Session()
        self._x = tf.placeholder(
            "float",
            [None, params['width'], params['height'], 6],
            name=self.network_name + '_x')
        self.q_t = tf.placeholder(
            "float",
            [None],
            name=self.network_name + '_q_t')
        self.actions = tf.placeholder(
            "float",
            [None, 4],
            name=self.network_name + '_actions')
        self.rewards = tf.placeholder("float",
                                      [None],
                                      name=self.network_name + '_rewards')
        self.terminals = tf.placeholder("float",
                                        [None],
                                        name=self.network_name + '_terminals')

        # Layer 1 (Convolutional)
        layer_name = 'conv1'
        size = 3
        channels = 6
        filters = 16
        stride = 1

        self.w_1 = tf.Variable(
            tf.random_normal([size, size, channels, filters], stddev=0.01),
            name=self.network_name + '_' + layer_name + '_weights')
        self.b_1 = tf.Variable(
            tf.constant(0.1, shape=[filters]),
            name=self.network_name + '_' + layer_name + '_biases')
        self.c_1 = tf.nn.conv2d(
            self._x,
            self.w_1,
            strides=[1, stride, stride, 1],
            padding='SAME',
            name=self.network_name+'_'+layer_name+'_convs')
        self.o_1 = tf.nn.relu(
            tf.add(self.c_1, self.b_1),
            name=self.network_name+'_'+layer_name+'_activations')

        # Layer 2 (Convolutional)
        layer_name = 'conv2'
        size = 3
        channels = 16
        filters = 32
        stride = 1

        self.w_2 = tf.Variable(
            tf.random_normal([size, size, channels, filters], stddev=0.01),
            name=self.network_name+'_'+layer_name+'_weights')
        self.b_2 = tf.Variable(
            tf.constant(0.1, shape=[filters]),
            name=self.network_name + '_' + layer_name + '_biases')
        self.c_2 = tf.nn.conv2d(
            self.o_1,
            self.w_2,
            strides=[1, stride, stride, 1],
            padding='SAME',
            name=self.network_name+'_'+layer_name+'_convs')
        self.o_2 = tf.nn.relu(
            tf.add(self.c_2, self.b_2),
            name=self.network_name+'_'+layer_name+'_activations')

        o2_shape = self.o_2.get_shape().as_list()

        # Layer 3 (Fully connected)
        layer_name = 'fc3'
        hiddens = 256
        dim = o2_shape[1] * o2_shape[2] * o2_shape[3]
        self.o2_flat = tf.reshape(
            self.o_2,
            [-1, dim],
            name=self.network_name+'_'+layer_name+'_input_flat')
        self.w_3 = tf.Variable(
            tf.random_normal([dim, hiddens], stddev=0.01),
            name=self.network_name+'_'+layer_name+'_weights')
        self.b_3 = tf.Variable(
            tf.constant(0.1, shape=[hiddens]),
            name=self.network_name+'_'+layer_name+'_biases')
        self.ip3 = tf.add(tf.matmul(self.o2_flat, self.w_3),
                          self.b_3,
                          name=self.network_name + '_' + layer_name + '_ips')
        self.o_3 = tf.nn.relu(
            self.ip3,
            name=self.network_name + '_' + layer_name + '_activations')

        # Layer 4
        layer_name = 'fc4'
        hiddens = 4
        dim = 256
        self.w_4 = tf.Variable(
            tf.random_normal([dim, hiddens], stddev=0.01),
            name=self.network_name + '_' + layer_name + '_weights')
        self.b_4 = tf.Variable(
            tf.constant(0.1, shape=[hiddens]),
            name=self.network_name+'_'+layer_name+'_biases')
        self._y = tf.add(
            tf.matmul(self.o_3, self.w_4),
            self.b_4,
            name=self.network_name+'_'+layer_name+'_outputs')

        # Q,Cost,Optimizer
        self.discount = tf.constant(self.params['discount'])
        self.y_j = tf.add(
            self.rewards,
            tf.multiply(1.0-self.terminals,
                        tf.multiply(self.discount, self.q_t)))
        self.q_pred = tf.reduce_sum(tf.multiply(self._y, self.actions),
                                    reduction_indices=1)
        self.cost = tf.reduce_sum(tf.pow(
            tf.subtract(self.y_j, self.q_pred), 2))

        if self.params['load_file'] is not None:
            self.global_step = tf.Variable(
                int(self.params['load_file'].split('_')[-1]),
                name='global_step',
                trainable=False)
        else:
            self.global_step = tf.Variable(0,
                                           name='global_step',
                                           trainable=False)

        self.optim = tf.train.AdamOptimizer(
            self.params['lr']).minimize(self.cost,
                                        global_step=self.global_step)
        self.saver = tf.train.Saver(max_to_keep=0)

        self.sess.run(tf.global_variables_initializer())

        if self.params['load_file'] is not None:
            print('Loading checkpoint...')
            self.saver.restore(self.sess, self.params['load_file'])

    def train(self, bat_s, bat_a, bat_t, bat_n, bat_r):
        """Specifrom_y Training Parameters

        Parameters
        ----------
        bat_s
        bat_a
        bat_t
        bat_n
        bat_r

        Returns
        -------
        cnt
        cost

        """
        feed_dict = {self._x: bat_n,
                     self.q_t: np.zeros(bat_n.shape[0]),
                     self.actions: bat_a,
                     self.terminals: bat_t,
                     self.rewards: bat_r}
        q_t = self.sess.run(self._y,
                            feed_dict=feed_dict)
        q_t = np.amax(q_t, axis=1)
        feed_dict = {self._x: bat_s,
                     self.q_t: q_t,
                     self.actions: bat_a,
                     self.terminals: bat_t,
                     self.rewards: bat_r}
        _, cnt, cost = self.sess.run(
            [self.optim, self.global_step, self.cost],
            feed_dict=feed_dict)
        return cnt, cost

    def save_ckpt(self, filename):
        """
        Parameters
        ----------
        filename
        """
        self.saver.save(self.sess, filename)
