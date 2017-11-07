# -*- coding: utf-8 -*-
"""
Created on Thu Oct 26 15:18:01 2017

@author: ellio
"""

import tensorflow as tf
import numpy as np
import os
import time as t
import matplotlib.pyplot as plt

#%%Load Data
#file Path for functions
funcPath = 'C:/Users/ellio/OneDrive/Documents/GitHub/ML-for-Chinese-Calligraphy/dataHandling'
os.chdir(funcPath)
from classFileFunctions import fileFunc as fF 
os.chdir("..")

#set ration of data to be training and testing
trainRatio = 0.9
numOutputs = 3755

def oneHot(numberList,n):
    oneHotArray=np.zeros((len(numberList),n));
    for j in range(len(numberList)):
        oneHotArray[j][numberList[j]] = 1;
    return oneHotArray;
#file path for data

print("splitting data...")
startTime=t.time()
#file to open
dataPath = 'C:/Users/ellio/Documents/training data/Machine Learning data/'
fileName="3Files-charNums-images"
labels,images=fF.readNPZ(dataPath,fileName,"saveLabels","saveImages")
dataLength=len(labels)
#split the data into training and testing
#train data
trainLabels = labels[0:int(dataLength*trainRatio)]
trainImages = images[0:int(dataLength*trainRatio)]
#test data
testLabels =  oneHot(labels[int(dataLength*trainRatio):dataLength],numOutputs)
testImages =images[int(dataLength*trainRatio):dataLength]
labels = 0;
images = 0;
print("took ",t.time()-startTime," seconds\n")

#%%
print("Building network...")
startTime=t.time()
#Functions to initialise weights to non-zero values 
def weight_variable(shape):
  initial = tf.truncated_normal(shape, stddev=0.1)
  return tf.Variable(initial)
def bias_variable(shape):
  initial = tf.constant(0.1, shape=shape)
  return tf.Variable(initial)
#functions to perform convolution and pooling operations
def conv2d(x, W):
  return tf.nn.conv2d(x, W, strides=[1, 1, 1, 1], padding='SAME')

def max_pool_2x2(x):
  return tf.nn.max_pool(x, ksize=[1, 2, 2, 1],
                        strides=[1, 2, 2, 1], padding='SAME')
  

    

#create place holders for nodes(inputs and labels)
x = tf.placeholder(tf.float32, shape=[None, 1600])
y_ = tf.placeholder(tf.float32, shape=[None,numOutputs])
#create variebles for the wieghts and biases
x_image = tf.reshape(x, [-1, 40, 40, 1])
#1st conv layer
W_conv1 = weight_variable([9, 9, 1, 32])#layer weights
b_conv1 = bias_variable([32])#layer bias
h_conv1 = tf.nn.relu(conv2d(x_image, W_conv1) + b_conv1)#layer output
#1st pooling layer
h_pool1 = max_pool_2x2(h_conv1)
#second conv layer
W_conv2 = weight_variable([9, 9, 32, 64])
b_conv2 = bias_variable([64])
h_conv2 = tf.nn.relu(conv2d(h_pool1, W_conv2) + b_conv2)
#second pool
h_pool2 = max_pool_2x2(h_conv2)
#flatten 
h_flatten = tf.reshape(h_pool2, [-1, 10*10*64])
#fully connected layer
W_fc1 = weight_variable([10 * 10 * 64, 1024])
b_fc1 = bias_variable([1024])
h_fc1 = tf.nn.relu(tf.matmul(h_flatten, W_fc1) + b_fc1)
#dropout layer
keep_prob = tf.placeholder(tf.float32)
h_drop1 = tf.nn.dropout(h_fc1, keep_prob)
#fully connected layer 2
W_fc2 = weight_variable([1024, numOutputs])
b_fc2 = bias_variable([numOutputs])

y_conv = tf.matmul(h_drop1, W_fc2) + b_fc2

#%%TRAINING

#training parameters
batchSize = 50
iterations = 70000
displayNum = 100
testNum = 500
#caluclate the average cross entropy across a batch between the predictions y_ and the labels y.
#This is the value to reduce
cross_entropy = tf.reduce_mean(
    tf.nn.softmax_cross_entropy_with_logits(labels=y_, logits=y_conv))
# define the training method to update the wieghts 
train_step = tf.train.GradientDescentOptimizer(1e-4).minimize(cross_entropy) 
#caluclate whether the prediction for each image is correct
correct_prediction = tf.equal(tf.argmax(y_conv,1), tf.argmax(y_,1))
#caluclate the average of all the predictions to get a factional accuracy
accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))
print("took ",t.time()-startTime," seconds\n")
print("start training")
startTime=t.time()
with tf.Session() as sess:
    sess.run(tf.global_variables_initializer())
# put through all training data and update the weights for each batch
    i=0
    testAccuracy= np.zeros(int(iterations/(testNum)))
    print("took ",t.time()-startTime," seconds\n")
    while i<iterations:
        print("ITERATION: ",i,"\n------------------------")
        iterationStart = t.time()
        #print("creating batch images...")
        #startTime=t.time()
        batchImages = trainImages[i%dataLength:i%dataLength+batchSize]
       # print("took ",t.time()-startTime," seconds\n")
        #print("creating batch labels...")
        #startTime=t.time()
        batchLabels = oneHot(trainLabels[i%dataLength:i%dataLength+batchSize],numOutputs)
        #print("took ",t.time()-startTime," seconds\n")
    #print training accuracy for every 100 iterations
        if i % (displayNum) == 0:
            print("evaluating training accuracy...")
            #startTime=t.time()
            train_accuracy = accuracy.eval(feed_dict={x: batchImages, y_: batchLabels, keep_prob: 1.0})
            print('step %d, training accuracy %g' % (i, train_accuracy))
            #print("took ",t.time()-startTime," seconds\n")
        if i%(testNum) == 0 and i!=0:
            print("evaluating test accuracy...")
            #startTime=t.time()
            test_accuracy = accuracy.eval(feed_dict={x: testImages, y_: testLabels, keep_prob: 1.0})
            print('test accuracy %g' % test_accuracy)
            testAccuracy[int(i/(testNum))]=test_accuracy
            #print("took ",t.time()-startTime," seconds\n")
        #print("running batch...")
        #startTime=t.time()
        train_step.run(feed_dict={x: batchImages, y_: batchLabels, keep_prob: 0.5})
        #print("took ",t.time()-startTime," seconds\n")
        print("Iterations ",i,"-",i+batchSize," took ",t.time()-iterationStart," seconds\n")
        i+=batchSize
    
plt.plot(testAccuracy)
plt.show()
    
