import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import os

from data.load import mnist
from nets.mlp import *
from utils import *


class eb_gan:
    def __init__(self, generator, discriminator, data, sess, height = 28, width = 28, iters = 1000000):
        self.x_dim = height * width
        self.y_dim = 10
        self.z_dim = 100
        self.h_dim = 128

        self.batch_size = 32
        self.learning_rate = 1e-4
        self.iters = iters

        self.margin = 5

        self.sess = sess

        self.generator = generator
        self.discriminator = discriminator
        self.data = data

        self.generator.set(self.x_dim, self.h_dim)
        self.discriminator.set(self.x_dim, self.h_dim)
        self.build_model()


    def build_model(self):
        self.x = tf.placeholder(tf.float32, shape = [None, self.x_dim])
        self.z = tf.placeholder(tf.float32, shape = [None, self.z_dim])
        self.k = tf.placeholder(tf.float32)

        self.g_sample = self.generator(self.z)
        self.d_real = self.discriminator(self.x)
        self.d_fake = self.discriminator(self.g_sample, reuse = True)

        self.d_loss = d_real - tf.maximum(self.margin - d_fake, 0.)
        self.g_loss = d_fake


    def train(self):
        d_solver = tf.train.AdamOptimizer(self.learning_rate).minimize(self.d_loss, var_list = self.discriminator.vars)
        g_solver = tf.train.AdamOptimizer(self.learning_rate).minimize(self.g_loss, var_list = self.generator.vars)

        self.sess.run(tf.global_variables_initializer())

        if not os.path.exists('out/'):
            os.makedirs('out/')

        i = 0
        for it in range(self.iters):
            if it % 1000 == 0:
                samples = sess.run(self.g_sample, feed_dict = {self.z: sample_z(16, self.z_dim)})
                fig = data2img(samples)
                plt.savefig('out/{}.png'.format(str(i).zfill(3)), bbox_inches = 'tight')
                i += 1
                plt.close(fig)
    
            x_batch, _ = self.data.next_batch(self.batch_size)
            x_batch = np.reshape(x_batch, (-1, self.x_dim))

            _, d_loss_cur = sess.run([d_solver, self.d_loss], feed_dict = {self.x: x_batch, self.z: sample_z(self.batch_size, self.z_dim)})
            _, g_loss_cur = sess.run([g_solver, self.g_loss], feed_dict = {self.z: sample_z(self.batch_size, self.z_dim)})

            if it % 1000 == 0:
                print('Iter: {}'.format(it))
                print('d_loss: {:.4}'. format(d_loss_cur))
                print('g_loss: {:.4}'. format(g_loss_cur))
                print()


    def _pullaway_loss(self, emb):
        norm = tf.sqrt(tf.reduce_sum(emb ** 2, 1, keep_dims = True))
        normalized_emb = emb / norm
        similarity = tf.matmul(normalized_emb, normalized_emb, transpose_b = True)
        batch_size = tf.cast(tf.shape(emb)[0], tf.float32)
        pt_loss = (tf.reduce_sum(similarity) - batch_size) / (batch_size * (batch_size - 1)) 

        return pt_loss


if __name__ == '__main__':
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

    generator = g_mlp_mnist()
    discriminator = d_mlp_autoencoder_mnist()
    data = mnist()

    sess = tf.Session()

    gan = eb_gan(generator, discriminator, data, sess)
    gan.train()

