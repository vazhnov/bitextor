#!/usr/bin/env python3

import numpy as np
import pylab as plt
import tensorflow as tf
import random
from collections import namedtuple

######################################################################################
class LearningParams:
    def __init__(self):
        self.gamma = 0.99 #0.1
        self.lrn_rate = 0.1
        self.max_epochs = 3 #0001
        self.eps = 1  # 0.7

######################################################################################
class Qnetwork():
    def __init__(self, lrn_rate, env):
        # These lines establish the feed-forward part of the network used to choose actions
        EMBED_DIM = 80

        NUM_ACTIONS = 5
        INPUT_DIM = EMBED_DIM // NUM_ACTIONS

        HIDDEN_DIM = 128

        # EMBEDDINGS
        self.embeddings = tf.Variable(tf.random_uniform([env.ns, INPUT_DIM], 0, 0.01))

        self.input = tf.placeholder(shape=[None, NUM_ACTIONS], dtype=tf.int32)
        #self.input1Hot = tf.one_hot(self.input, env.ns)

        self.embedConcat = tf.nn.embedding_lookup(self.embeddings, self.input)
        self.embedConcat = tf.reshape(self.embedConcat, [tf.shape(self.input)[0], EMBED_DIM])
        self.embedding = self.embedConcat

        #self.embedding = tf.matmul(self.input1Hot, self.embeddings)
        #self.embedding = tf.math.multiply(self.embedding, 0.1)
        self.embedding = tf.math.l2_normalize(self.embedding, axis=1)

        # HIDDEN 1
        #self.embedding = tf.placeholder(shape=[1, env.ns], dtype=tf.float32)
        self.hidden1 = self.embedding

        self.Whidden1 = tf.Variable(tf.random_uniform([EMBED_DIM, EMBED_DIM], 0, 0.01))
        #self.Whidden1 = tf.nn.softmax(self.Whidden1, axis=1)
        #self.Whidden1 = tf.nn.sigmoid(self.Whidden1)
        #self.Whidden1 = tf.math.l2_normalize(self.Whidden1, axis=1)

        self.hidden1 = tf.matmul(self.hidden1, self.Whidden1)
        #self.hidden1 = tf.nn.softmax(self.hidden1, axis=1)
        #self.hidden1 = tf.nn.sigmoid(self.hidden1)

        #self.BiasHidden1 = tf.Variable(tf.random_uniform([1, EMBED_DIM], 0, 0.01))
        #self.hidden1 = tf.add(self.hidden1, self.BiasHidden1)

        self.hidden1 = tf.math.l2_normalize(self.hidden1, axis=1)
        #self.hidden1 = tf.nn.relu(self.hidden1)

        # HIDDEN
        #self.embedding = tf.placeholder(shape=[1, env.ns], dtype=tf.float32)
        self.hidden2 = self.hidden1

        self.Whidden2 = tf.Variable(tf.random_uniform([EMBED_DIM, HIDDEN_DIM], 0, 0.01))
        #self.Whidden = tf.nn.softmax(self.Whidden, axis=1)
        #self.Whidden = tf.nn.sigmoid(self.Whidden)
        #self.Whidden = tf.math.l2_normalize(self.Whidden, axis=1)
        self.hidden2 = tf.matmul(self.hidden2, self.Whidden2)

        #self.Whidden = tf.Variable(tf.random_uniform([1, env.ns], 0, 0.01))
        #self.Whidden = tf.nn.softmax(self.Whidden, axis=1)
        #self.Whidden = tf.nn.sigmoid(self.Whidden)
        #self.Whidden = tf.clip_by_value(self.Whidden, -10, 10)
        #self.hidden = tf.multiply(self.hidden, self.Whidden)

        self.BiasHidden2 = tf.Variable(tf.random_uniform([1, HIDDEN_DIM], 0, 0.01))
        #self.BiasHidden = tf.nn.softmax(self.BiasHidden, axis=1)
        #self.BiasHidden = tf.nn.sigmoid(self.BiasHidden)
        #self.BiasHidden = tf.math.l2_normalize(self.BiasHidden, axis=1)
        self.hidden2 = tf.add(self.hidden2, self.BiasHidden2)

        # OUTPUT
        self.Wout = tf.Variable(tf.random_uniform([HIDDEN_DIM, 5], 0, 0.01))
        #self.W = tf.math.l2_normalize(self.W, axis=1)
        #self.W = tf.nn.sigmoid(self.W)
        #self.W = tf.math.multiply(self.W, 2)
        #self.W = tf.clip_by_value(self.W, -10, 10)

        self.Qout = tf.matmul(self.hidden2, self.Wout)
        #self.Qout = tf.clip_by_value(self.Qout, -10, 10)
        #self.Qout = tf.nn.sigmoid(self.Qout)
        self.Qout = tf.math.multiply(self.Qout, 0.1)

        self.predict = tf.argmax(self.Qout, 1)

        # Below we obtain the loss by taking the sum of squares difference between the target and prediction Q values.
        self.nextQ = tf.placeholder(shape=[None, 5], dtype=tf.float32)
        self.loss = tf.reduce_sum(tf.square(self.nextQ - self.Qout))
        self.trainer = tf.train.GradientDescentOptimizer(learning_rate=lrn_rate)
        self.updateModel = self.trainer.minimize(self.loss)

    def PrintQ(self, curr, env, sess):
        # print("hh", next, hh)
        neighbours = env.GetNeighBours(curr)
        a, allQ = sess.run([self.predict, self.Qout], feed_dict={self.input: neighbours})
        print("curr=", curr, "a=", a, "allQ=", allQ, neighbours)

    def PrintAllQ(self, env, sess):
        for curr in range(env.ns):
            self.PrintQ(curr, env, sess)

######################################################################################
# helpers
class Env:
    def __init__(self):
        self.goal = 14
        self.ns = 16  # number of states

        self.F = np.zeros(shape=[self.ns, self.ns], dtype=np.int)  # Feasible
        self.F[0, 1] = 1;
        self.F[0, 5] = 1;
        self.F[1, 0] = 1;
        self.F[2, 3] = 1;
        self.F[3, 2] = 1
        self.F[3, 4] = 1;
        self.F[3, 8] = 1;
        self.F[4, 3] = 1;
        self.F[4, 9] = 1;
        self.F[5, 0] = 1
        self.F[5, 6] = 1;
        self.F[5, 10] = 1;
        self.F[6, 5] = 1;
        # self.F[6, 7] = 1; # hole
        # self.F[7, 6] = 1; # hole
        self.F[7, 8] = 1;
        self.F[7, 12] = 1
        self.F[8, 3] = 1;
        self.F[8, 7] = 1;
        self.F[9, 4] = 1;
        self.F[9, 14] = 1;
        self.F[10, 5] = 1
        self.F[10, 11] = 1;
        self.F[11, 10] = 1;
        self.F[11, 12] = 1;
        self.F[12, 7] = 1;
        self.F[12, 11] = 1;
        self.F[12, 13] = 1;
        self.F[13, 12] = 1;

        for i in range(self.ns):
            self.F[i, self.ns - 1] = 1
        #print("F", self.F)

    def GetNextState(self, curr, action, neighbours):
        #print("curr", curr, action, neighbours)
        next = neighbours[0, action]
        assert(next >= 0)
        #print("next", next)

        done = False
        if next == self.goal:
            reward = 8.5
            done = True
        elif next == self.ns - 1:
            reward = 0
            done = True
        else:
            reward = -1

        return next, reward, done

    def GetNeighBours(self, curr):
        col = self.F[curr, :]
        ret = []
        for i in range(len(col)):
            if col[i] == 1:
                ret.append(i)

        for i in range(len(ret), 5):
            ret.append(self.ns - 1)

        random.shuffle(ret)

        #ret = np.empty([5,1])
        ret = np.array(ret)
        ret = ret.reshape([1, 5])
        #print("GetNeighBours", ret.shape, ret)

        return ret

    def Walk(self, start, sess, qn, printQ):
        curr = start
        i = 0
        totReward = 0
        print(str(curr) + "->", end="")
        while True:
            # print("curr", curr)
            # print("hh", next, hh)
            neighbours = self.GetNeighBours(curr)
            action, allQ = sess.run([qn.predict, qn.Qout], feed_dict={qn.input: neighbours})
            action = action[0]
            next, reward, done = self.GetNextState(curr, action, neighbours)
            totReward += reward

            if printQ:
                print("printQ", action, allQ, neighbours)

            print("(" + str(action) + ")", str(next) + "(" + str(reward) + ") -> ", end="")
            # print(str(next) + "->", end="")
            curr = next

            if done: break
            if curr == self.goal: break

            i += 1
            if i > 50:
                print("LOOPING")
                break

        print("done", totReward)

    def WalkAll(self, sess, qn):
        for start in range(self.ns):
            self.Walk(start, sess, qn, False)

######################################################################################

def Neural(epoch, curr, params, env, sess, qn):
    # NEURAL
    # print("hh", next, hh)
    neighbours = env.GetNeighBours(curr)
    a, allQ = sess.run([qn.predict, qn.Qout], feed_dict={qn.input: neighbours})
    a = a[0]
    if np.random.rand(1) < params.eps:
        a = np.random.randint(0, 5)

    next, r, done = env.GetNextState(curr, a, neighbours)
    #print("curr=", curr, "a=", a, "next=", next, "r=", r, "allQ=", allQ)

    # Obtain the Q' values by feeding the new state through our network
    if curr == env.ns - 1:
        targetQ = np.zeros([1, 5])
        maxQ1 = 0
    else:
        # print("  hh2", hh2)
        nextNeighbours = env.GetNeighBours(next)
        Q1 = sess.run(qn.Qout, feed_dict={qn.input: nextNeighbours})
        # print("  Q1", Q1)
        maxQ1 = np.max(Q1)

        #targetQ = allQ
        targetQ = np.array(allQ, copy=True)
        #print("  targetQ", targetQ)
        targetQ[0, a] = r + params.gamma * maxQ1
        #print("  targetQ", targetQ)

    #print("  targetQ", targetQ, maxQ1)
    #print("  new Q", a, allQ)

    Transition = namedtuple("Transition", "curr next done neighbours targetQ")
    transition = Transition(curr, next, done, neighbours, targetQ)

    return transition

def UpdateQN(params, env, sess, epoch, qn, neighbours, targetQ):
    if epoch % 10000 == 0:
        outs = [qn.updateModel, qn.Wout, qn.Whidden2, qn.BiasHidden2, qn.Qout, qn.embeddings, qn.embedConcat]
        _, W, Whidden, BiasHidden, Qout, embeddings, embedConcat = sess.run(outs,
                                                                            feed_dict={qn.input: neighbours,
                                                                                       qn.nextQ: targetQ})
        print("epoch", epoch)
        #print("embeddings", embeddings)
        #print("embedConcat", embedConcat.shape)

        #print("  W\n", W)
        #print("  Whidden\n", Whidden)
        #print("  BiasHidden\n", BiasHidden)
        qn.PrintAllQ(env, sess)
        env.WalkAll(sess, qn)
        env.Walk(9, sess, qn, True)

        #print("curr", curr, "next", next, "action", a)
        #print("allQ", allQ)
        #print("targetQ", targetQ)
        #print("Qout", Qout)
        print("eps", params.eps)

        print()
    else:
        sess.run([qn.updateModel], feed_dict={qn.input: neighbours, qn.nextQ: targetQ})


def Trajectory(epoch, curr, params, env, sess, qn):
    path = []
    while (True):
        transition = Neural(epoch, curr, params, env, sess, qn)
        path.append(transition)
        curr = transition.next

        if transition.done: break
    #print()

    trajSize = len(path)
    trajNeighbours = np.empty([trajSize, 5])
    trajTargetQ = np.empty([trajSize, 5])

    i = 0
    for transition in path:
        #print("transition", transition.neighbours.shape, transition.targetQ.shape)
        trajNeighbours[i, :] = transition.neighbours
        trajTargetQ[i, :] = transition.targetQ
        #UpdateQN1(params, env, sess, epoch, qn, transition)

        i += 1
    #print("path", len(path), path)
    #print("   batchNeighbours", batchNeighbours)
    #print("   batchTargetQ", batchTargetQ)
    return curr, path, trajNeighbours, trajTargetQ

def Train(params, env, sess, qn):
    scores = []

    maxBatchSize = 2
    batchSize = 0

    trajectories = []
    for epoch in range(params.max_epochs):
        curr = np.random.randint(0, env.ns)  # random start state
        stopState, path, trajNeighbours, trajTargetQ = Trajectory(epoch, curr, params, env, sess, qn)
        #print("stopState", stopState, trajNeighbours.shape, trajTargetQ.shape)
        assert(trajNeighbours.shape[0] == trajTargetQ.shape[0])
        assert(5 == trajNeighbours.shape[1] == trajTargetQ.shape[1])
        trajSize = trajNeighbours.shape[0]

        if batchSize + trajSize > maxBatchSize:
            print("trajectories", len(trajectories), trajectories)
            print("batchSize", batchSize)
            batchNeighbours = np.empty([batchSize, 5])
            batchTargetQ = np.empty([batchSize, 5])

            row = 0
            for trajectory in trajectories:
                path2, trajNeighbours2, trajTargetQ2 = trajectory
                print("path2", path2)
                
                trajSize2 = trajNeighbours2.shape[0]
                batchNeighbours[row:row+trajSize2, :] = trajNeighbours2
                batchTargetQ[row:row+trajSize2, :] = trajTargetQ2

                row += trajSize2

            print("batchNeighbours", batchNeighbours.shape, batchNeighbours)
            print("batchTargetQ", batchTargetQ.shape, batchTargetQ)
            UpdateQN(params, env, sess, epoch, qn, batchNeighbours, batchTargetQ)

            trajectories = []
            batchSize = 0

        # add to batch
        ele = (path, trajNeighbours, trajTargetQ)
        trajectories.append(ele)

        batchSize += trajSize

        if stopState == env.goal:
            #eps = 1. / ((i/50) + 10)
            params.eps *= .999
            params.eps = max(0.1, params.eps)
            #print("eps", params.eps)

    return scores

######################################################################################

######################################################################################

def Main():
    print("Starting")
    np.random.seed()
    np.set_printoptions(formatter={'float': lambda x: "{0:0.5f}".format(x)})

    # =============================================================
    env = Env()

    params = LearningParams()

    tf.reset_default_graph()
    qn = Qnetwork(params.lrn_rate, env)
    init = tf.global_variables_initializer()
    print("qn.Qout", qn.Qout)

    with tf.Session() as sess:
        sess.run(init)

        scores = Train(params, env, sess, qn)
        print("Trained")

        qn.PrintAllQ(env, sess)
        env.WalkAll(sess, qn)

        # plt.plot(scores)
        # plt.show()

    print("Finished")


if __name__ == "__main__":
    Main()
