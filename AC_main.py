import tensorflow as tf
import numpy as np
import gym
from user_environment import envr
np.random.seed(2)
tf.set_random_seed(2)  # reproducible


class Actor(object):
    def __init__(self, sess, n_features, action_bound, lr=0.001):
        self.sess = sess
        self.s = tf.placeholder(tf.float32, [1, n_features], "state")
        self.a = tf.placeholder(tf.float32, None, name="act")
        self.td_error = tf.placeholder(tf.float32, None, name="td_error")  # TD_error

        l1 = tf.layers.dense(
            inputs=self.s,
            units=30,  # number of hidden units
            activation=tf.nn.relu,
            kernel_initializer=tf.random_normal_initializer(0., .1),  # weights
            bias_initializer=tf.constant_initializer(0.1),  # biases
            name='l1'
        )

        mu1 = tf.layers.dense(
            inputs=l1,
            units=1,  # number of hidden units
            activation=tf.nn.tanh,
            kernel_initializer=tf.random_normal_initializer(0., .1),  # weights
            bias_initializer=tf.constant_initializer(0.1),  # biases
            name='mu1'
        )

        sigma1 = tf.layers.dense(
            inputs=l1,
            units=1,  # output units
            activation=tf.nn.softplus,  # get action probabilities
            kernel_initializer=tf.random_normal_initializer(0., .1),  # weights
            bias_initializer=tf.constant_initializer(1.),  # biases
            name='sigma1'
        )
        mu2 = tf.layers.dense(
            inputs=l1,
            units=1,  # number of hidden units
            activation=tf.nn.tanh,
            kernel_initializer=tf.random_normal_initializer(0., .1),  # weights
            bias_initializer=tf.constant_initializer(0.1),  # biases
            name='mu2'
        )

        sigma2 = tf.layers.dense(
            inputs=l1,
            units=1,  # output units
            activation=tf.nn.softplus,  # get action probabilities
            kernel_initializer=tf.random_normal_initializer(0., .1),  # weights
            bias_initializer=tf.constant_initializer(1.),  # biases
            name='sigma2'
        )
        global_step = tf.Variable(0, trainable=False)
        # self.e = epsilon = tf.train.exponential_decay(2., global_step, 1000, 0.9)
        self.mu1, self.sigma1 = tf.squeeze(mu1), tf.squeeze(sigma1)
        self.mu2, self.sigma2 = tf.squeeze(mu2), tf.squeeze(sigma2)
        tfd = tf.contrib.distributions
        self.normal_dist = tfd.MultivariateNormalDiag(
            loc=[self.mu1,self.mu2],
            scale_diag=[self.sigma1,self.sigma2])
        self.action = tf.clip_by_value(self.normal_dist.sample(1), action_bound[0], action_bound[1])

        with tf.name_scope('exp_v'):
            log_prob = self.normal_dist.log_prob(self.a)  # loss without advantage
            self.exp_v = log_prob * self.td_error  # advantage (TD_error) guided loss
            # Add cross entropy cost to encourage exploration
            self.exp_v += 0.01*self.normal_dist.entropy()

        with tf.name_scope('train'):
            self.train_op = tf.train.AdamOptimizer(lr).minimize(-self.exp_v, global_step)    # min(v) = max(-v)

    def learn(self, s, a, td):
        s = s[np.newaxis, :]
        feed_dict = {self.s: s, self.a: a, self.td_error: td}
        _, exp_v = self.sess.run([self.train_op, self.exp_v], feed_dict)
        return exp_v

    def choose_action(self, s):
        s = s[np.newaxis, :]
        return self.sess.run(self.action, {self.s: s})  # get probabilities for all actions


class Critic(object):
    def __init__(self, sess, n_features, lr=0.01):
        self.sess = sess
        with tf.name_scope('inputs'):
            self.s = tf.placeholder(tf.float32, [1, n_features], "state")
            self.v_ = tf.placeholder(tf.float32, [1, 1], name="v_next")
            self.r = tf.placeholder(tf.float32, name='r')
            self.a=tf.placeholder(tf.float32,[1,2],name='cri_a')
            self.a_=tf.placeholder(tf.float32,[1,2],name='cri_a_')

        with tf.variable_scope('Critic'):
            l1 = tf.layers.dense(
                inputs=tf.concat([self.s,self.a],axis=-1),
                units=60,  # number of hidden units
                activation=tf.nn.relu,
                kernel_initializer=tf.random_normal_initializer(0., .1),  # weights
                bias_initializer=tf.constant_initializer(0.1),  # biases
                name='l1'
            )
            l2 = tf.layers.dense(
                inputs=l1,
                units=30,  # number of hidden units
                activation=tf.nn.relu,
                kernel_initializer=tf.random_normal_initializer(0., .1),  # weights
                bias_initializer=tf.constant_initializer(0.1),  # biases
                name='l2'
            )

            self.v = tf.layers.dense(
                inputs=l2,
                units=1,  # output units
                activation=None,
                kernel_initializer=tf.random_normal_initializer(0., .1),  # weights
                bias_initializer=tf.constant_initializer(0.1),  # biases
                name='V'
            )

        with tf.variable_scope('squared_TD_error'):
            self.td_error = tf.reduce_mean(self.r + GAMMA * self.v_ - self.v)
            self.loss = tf.square(self.td_error)    # TD_error = (r+gamma*V_next) - V_eval
            tf.summary.scalar('loss', self.loss)
        with tf.variable_scope('train'):
            self.train_op = tf.train.AdamOptimizer(lr).minimize(self.loss)

    def learn(self, s, r, s_,i,a,a_):
        s, s_= s[np.newaxis, :], s_[np.newaxis, :]

        v_ = self.sess.run(self.v, {self.s: s_,self.a:a_})
        td_error, _ = self.sess.run([self.td_error, self.train_op],
                                          {self.s: s, self.v_: v_, self.r: r,self.a:a})
        merged = tf.summary.merge_all()
        result = self.sess.run(merged, {self.s: s, self.v_: v_, self.r: r,self.a:a})
        AC_writer.add_summary(result, i)
        return td_error


OUTPUT_GRAPH = True
MAX_EPISODE = 1000
MAX_EP_STEPS = 200
GAMMA = 0.9
LR_A = 0.001    # learning rate for actor
LR_C = 0.01     # learning rate for critic

env = envr()
N_S = 3
A_BOUND = 1
i=1

sess = tf.Session()

actor = Actor(sess, n_features=N_S, lr=LR_A, action_bound=[0, A_BOUND])
critic = Critic(sess, n_features=N_S, lr=LR_C)

sess.run(tf.global_variables_initializer())

if OUTPUT_GRAPH:
    AC_writer =tf.summary.FileWriter("logs/", sess.graph)

for i_episode in range(MAX_EPISODE):
    s = env.reset()
    t=1
    print('####新的次数####')
    while True:
        a = actor.choose_action(s)
        s_, r = env.step(s,a)
        a_ = actor.choose_action(s_)
        td_error = critic.learn(s, r*5, s_,i,a,a_)  # gradient = grad[r + gamma * V(s_) - V(s)]
        actor.learn(s, a, td_error)  # true_gradient = grad[logPi(s,a) * td_error]
        print('t:',t,'s:',s,'a:',a,'r:',r*5)
        s = s_
        t=t+1;i+=1
        if t==1000:
            break
