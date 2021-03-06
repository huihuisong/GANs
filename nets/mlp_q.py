import tensorflow as tf
import tensorflow.contrib as tc
import tensorflow.contrib.layers as tcl


class g_mlp_q_mnist():
    def __init__(self):
        self.name = 'g_mlp_mnist'


    def __call__(self, z, y = None):
        ins = z
        if y != None:
            ins = tf.concat(values = [z, y], axis = 1)

        with tf.variable_scope(self.name):
            g = tcl.fully_connected(ins, self.h_dim, activation_fn = tf.nn.relu, weights_initializer = tf.random_normal_initializer(0, 0.02))
            g = tcl.fully_connected(g, self.x_dim, activation_fn = tf.nn.sigmoid, weights_initializer = tf.random_normal_initializer(0, 0.02))

        return g


    def set(self, x_dim, h_dim):
        self.x_dim = x_dim
        self.h_dim = h_dim


    @property
    def vars(self):
        return tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, scope = self.name)


class d_mlp_q_mnist():
    def __init__(self):
        self.name = 'd_mlp_mnist'


    def __call__(self, x, reuse = False):
        with tf.variable_scope(self.name) as vs:
            if reuse:
                vs.reuse_variables()
            d = tcl.fully_connected(x, self.h_dim, activation_fn = tf.nn.relu, weights_initializer = tf.random_normal_initializer(0, 0.02))
            d_logit = tcl.fully_connected(d, 1, activation_fn = None, weights_initializer = tf.random_normal_initializer(0, 0.02))
            q_logit = tcl.fully_connected(d, self.c_dim, activation_fn = None, weights_initializer = tf.random_normal_initializer(0, 0.02))

        return d_logit, q_logit


    def set(self, h_dim, c_dim):
        self.h_dim = h_dim
        self.c_dim = c_dim


    @property
    def vars(self):
        return tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, scope = self.name)

