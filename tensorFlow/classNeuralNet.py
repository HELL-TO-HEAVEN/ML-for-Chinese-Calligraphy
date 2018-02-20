# -*- coding: utf-8 -*-
"""
Created on Tue Feb 20 13:06:57 2018

@author: ellio
"""
import tensorflow as tf        
        
class layer:
    def __init__(self,layerType,outputShape,output):
        self.layerType=layerType
        self.outputs=outputShape
        self.output = output
    def getOutputShape(self):
        return self.outputShape
    def getType(self):
        return self.layerType
    def getOutput(self):
        return self.output

class NeuralNet:
    def __init__(self):
        self.layers = []
        self.numFC=0
        self.numConv=0
        self.numReshape=0
        self.numDropout=0
        self.numRelu=0
        self.numPool=0
        
    def weight_variable(shape):
        """weight_variable generates a weight variable of a given shape."""
        initial = tf.truncated_normal(shape, stddev=0.1)
        tf.summary.histogram("weights", initial)
        return tf.Variable(initial)
    
    def bias_variable(shape):
        """bias_variable generates a bias variable of a given shape."""
        initial = tf.constant(0.1, shape=shape)
        tf.summary.histogram("biases", initial)
        return tf.Variable(initial)  
    
    def addConvLayer(self,outputs,kernelSize=5):
        prevOutput = self.layers[len(self.layers)-1].getOutput
        prevOutputShape = self.layers[len(self.layers)-1].getOutputShape
        prevType = self.layers[len(self.layers)-1].getType
        allowedPrevTypes=["reshape", "conv", "relu", "pool", "input"]
        if prevType not in allowedPrevTypes:
            print('Error: Cannot place layer of type [conv] after layer of type ',prevType)
        else:
            self.numConv+=1
            with tf.name_scope('Conv{}'.format(self.numConv)):
                with tf.name_scope("Weights"):
                    w_conv = self.weight_variable([kernelSize,kernelSize, prevOutputShape[2], outputs])
                with tf.name_scope("Bias"):
                    b_conv = self.bias_variable([outputs])
                with tf.name_scope("Convolve"):
                    h_conv = tf.nn.conv2d(prevOutput, w_conv, strides=[1, 1, 1, 1], padding='SAME') + b_conv
                    tf.summary.histogram("activations", h_conv)      
            self.layers.append(layer("conv",[prevOutputShape[0:2],outputs],h_conv))
     
    def addPoolLayer(self,kernelSize=2,stride = 2):
        prevOutput = self.layers[len(self.layers)-1].getOutput
        prevOutputShape = self.layers[len(self.layers)-1].getOutputShape
        prevType = self.layers[len(self.layers)-1].getType
        allowedPrevTypes=["conv", "input", "dropout", "relu"]
        if prevType not in allowedPrevTypes:
            print("Error: Cannot place layer of type [pool] after layer of type ",prevType)
        else:
            self.numpool+=1
            with tf.name_scope('Pool{}'.format(self.numPool)):
                h_pool=tf.nn.max_pool(prevOutput, ksize=[1, kernelSize, kernelSize, 1],strides=[1, stride, stride, 1], padding='SAME')
            self.layers.append(layer("pool",[prevOutputShape[0:2]/2,prevOutputShape[2]],h_pool))    
        
    def addFCLayer(self,outputs):
        prevOutput = self.layers[len(self.layers)-1].getOutput
        prevOutputShape = self.layers[len(self.layers)-1].getOutputShape
        prevType = self.layers[len(self.layers)-1].getType
        allowedPrevTypes=["reshape", "fc", "relu", "input"]
        if prevType not in allowedPrevTypes:
            print("Error: Cannot place layer of type [fc] after layer of type ",prevType)
        else:
            self.numFC+=1
            with tf.name_scope('FC{}'.format(self.numFC)):
                with tf.name_scope("Weights"):
                    w_fc = self.weight_variable([prevOutputShape[2], outputs])
                with tf.name_scope("Bias"):
                    b_fc = self.bias_variable([outputs])
                with tf.name_scope("MatMul"):
                    h_fc = tf.matMul(prevOutput, w_fc) + b_fc
                    tf.summary.histogram("activations", h_fc)      
            self.layers.append(layer("conv",[1,1,outputs],h_fc))
    
    def addReluLayer(self):
        prevOutput = self.layers[len(self.layers)-1].getOutput
        prevOutputShape = self.layers[len(self.layers)-1].getOutputShape
        prevType = self.layers[len(self.layers)-1].getType
        allowedPrevTypes=["reshape", "fc", "conv", "input", "dropout"]
        if prevType not in allowedPrevTypes:
            print("Error: Cannot place layer of type [Relu] after layer of type ",prevType)
        else:
            self.numRelu+=1
            with tf.name_scope('Relu{}'.format(self.numRelu)):
                h_relu=tf.nn.relu(prevOutput)
            self.layers.append(layer("relu",prevOutputShape,h_relu))
    def addReshapeLayer(self,outputShape):
        prevOutput = self.layers[len(self.layers)-1].getOutput
        prevOutputShape = self.layers[len(self.layers)-1].getOutputShape
        prevType = self.layers[len(self.layers)-1].getType
        allowedPrevTypes=["reshape", "fc", "conv", "input", "dropout","relu"]
        if