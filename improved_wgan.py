import tensorflow as tf
from tensorflow.examples.tutorials.mnist import input_data
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import os


def xavier_init(size):
    xavier_stddev = 1.0 / tf.sqrt(size[0] / 2.0)
    return tf.random_normal(shape = size, stddev = xavier_stddev)


X = tf.placeholder(tf.float32, shape = [None, 784])

D_W1 = tf.Variable(xavier_init([784, 128]))
D_b1 = tf.Variable(tf.zeros(shape = [128]))
D_W2 = tf.Variable(xavier_init([128, 1]))
D_b2 = tf.Variable(tf.zeros(shape = [1]))
theta_D = [D_W1, D_W2, D_b1, D_b2]

Z = tf.placeholder(tf.float32, shape = [None, 100])

G_W1 = tf.Variable(xavier_init([100, 128]))
G_b1 = tf.Variable(tf.zeros(shape = [128]))
G_W2 = tf.Variable(xavier_init([128, 784]))
G_b2 = tf.Variable(tf.zeros(shape = [784]))
theta_G = [G_W1, G_W2, G_b1, G_b2]


def sample_Z(m, n):
    return np.random.uniform(-1.0, 1.0, size = [m, n])


def generator(z):
    G_h1 = tf.nn.relu(tf.matmul(z, G_W1) + G_b1)
    G_log_prob = tf.matmul(G_h1, G_W2) + G_b2
    G_prob = tf.nn.sigmoid(G_log_prob)

    return G_prob


def discriminator(x):
    D_h1 = tf.nn.relu(tf.matmul(x, D_W1) + D_b1)
    out = tf.matmul(D_h1, D_W2) + D_b2

    return out


def plot(samples):
    fig = plt.figure(figsize = (4, 4))
    gs = gridspec.GridSpec(4, 4)
    gs.update(wspace = 0.05, hspace = 0.05)

    for i, sample in enumerate(samples):
        ax = plt.subplot(gs[i])
        plt.axis = 'off'
        ax.set_xticklabels([])
        ax.set_yticklabels([])
        ax.set_aspect('equal')
        plt.imshow(sample.reshape(28, 28), cmap = 'Greys_r')

    return fig


G_sample = generator(Z)

D_real = discriminator(X)
D_fake = discriminator(G_sample)

lam = 10

eps = tf.random_uniform([32, 1], minval = 0.0, maxval = 1.0)
X_inter = eps * X + (1.0 - eps) * G_sample
grad = tf.gradients(discriminator(X_inter), [X_inter])[0]
grad_norm = tf.sqrt(tf.reduce_sum(grad ** 2, axis = 1))
grad_pen = lam * tf.reduce_mean((grad_norm - 1) ** 2)

D_loss = -tf.reduce_mean(D_real) + tf.reduce_mean(D_fake) + grad_pen
G_loss = -tf.reduce_mean(D_fake)

D_solver = tf.train.AdamOptimizer(learning_rate = 1e-4, beta1 = 0.5).minimize(D_loss, var_list = theta_D)
G_solver = tf.train.AdamOptimizer(learning_rate = 1e-4, beta1 = 0.5).minimize(G_loss, var_list = theta_G)

mb_size = 32
Z_dim = 100

mnist = input_data.read_data_sets('../../MNIST_data', one_hot = True)

sess = tf.Session()
sess.run(tf.global_variables_initializer())

if not os.path.exists('out/'):
    os.makedirs('out/')

i = 0

for it in range(1000000):
    if it % 1000 == 0:
        samples = sess.run(G_sample, feed_dict = {Z: sample_Z(16, Z_dim)})

        fig = plot(samples)
        plt.savefig('out/{}.png'.format(str(i).zfill(3)), bbox_inches = 'tight')
        i += 1
        plt.close(fig)

    for _ in range(5):
        X_mb, _ = mnist.train.next_batch(mb_size)
        _, D_loss_curr = sess.run([D_solver, D_loss], feed_dict = {X: X_mb, Z: sample_Z(mb_size, Z_dim)})
    _, G_loss_curr = sess.run([G_solver, G_loss], feed_dict = {Z: sample_Z(mb_size, Z_dim)})

    if it % 1000 == 0:
        print('Iter: {}'.format(it))
        print('D_loss: {:.4}'. format(D_loss_curr))
        print('G_loss: {:.4}'.format(G_loss_curr))

        print()

