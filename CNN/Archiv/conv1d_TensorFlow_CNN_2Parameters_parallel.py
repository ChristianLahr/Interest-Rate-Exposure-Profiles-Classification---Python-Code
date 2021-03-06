#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May  4 11:42:39 2017

@author: Chris

A Convolutional Network implementation using TensorFlow library.
"""

# first define results, but only one time. Than all the results are archived there
# esults_two_param=[{}]
#%%

def randomizeRows(VectData, VectLabel_param1, VectLabel_param2):
    # brings the rows of both vectors in the same new random order
    # both vectors need same length
    indices = np.random.permutation(len(VectData))
    tempData = [VectData[i] for i in indices]
    tempLabel_param1 = [VectLabel_param1[i] for i in indices]
    tempLabel_param2 = [VectLabel_param2[i] for i in indices]
    return tempData, tempLabel_param1, tempLabel_param2
    
def loadDataFromCSV(path, normalize, maturityStyle, randomize): # normalize = True --> normalization over altitude of every row (=time series)
    # Import other test data
    completeData = pd.read_csv(path, header=None, sep=";")
    datapoints = completeData.iloc[:, : completeData.shape[1] - 4 ].values
    lables_param1 = completeData.iloc[:, completeData.shape[1] - 4 : completeData.shape[1] - 3 ].values
    lables_param2 = completeData.iloc[:, completeData.shape[1] - 1 : completeData.shape[1] - 0 ].values

    # transform the maturity text into integers 
#    for i, text in enumerate(lables):
#        if text == 'QUARTERLY':
#            lables[i] = 0            
#        if text == 'SEMIANNUAL':
#            lables[i] = 1            
#        if text == 'ANNUAL':
#            lables[i] = 2            

    # maturities labels have be of the form 1, 2, ...
    a = np.zeros((datapoints.shape[0], n_classes_param1)) 
    for i, number in enumerate(lables_param1):
        a[i][ int((number[0] - 1)/2) ] = 1        

    lables_Matrix_param1 = a

    a = np.zeros((datapoints.shape[0], n_classes_param2)) 
    for i, number in enumerate(lables_param2):
        a[i][ int(number[0] - 0) ] = 1        

    lables_Matrix_param2 = a
    
    if normalize == True:
        for i in range(0, datapoints.shape[0]):
            maximum = np.ndarray.max(datapoints[i])
            for j in range(0, datapoints.shape[1]):
                datapoints[i][j] = (datapoints[i][j] / maximum)

    # randomize order
    if randomize == True:
        datapoints_rand_list, lables_rand_list_param1, lables_rand_list_param2 = randomizeRows(datapoints, lables_Matrix_param1, lables_Matrix_param2)
        datapoints_rand = np.float32(datapoints_rand_list)
        lables_rand_param1 = np.float32(lables_rand_list_param1)
        lables_rand_param2 = np.float32(lables_rand_list_param2)
    print('Data loaded')
    return datapoints_rand, lables_rand_param1, lables_rand_param2
#%%

import tensorflow as tf
import pandas as pd
import numpy as np

#tf.reset_default_graph()

# Parameters
learning_rate = 0.001
training_iters = 20000
batch_size = 128
display_step = 4

maturityStyle = 'normal'

# Network Parameters
n_input = 120 # time series data input shape: 120 data points
dropout = 0.75 # Dropout, probability to keep units
conv1Kernal_size = 15
conv1Feature_Number = 32
conv2Kernal_size = 40
conv2Feature_Number = 64

n_classes_param1 = 15
n_classes_param2 = 12


file1Name = '/Users/Chris/Python/Machine Learning/Masterarbeit1/Exposure0.05Quantile16052017_coupon_frequency_maturity.csv'
file2Name = '/Users/Chris/Python/Machine Learning/Masterarbeit1/Exposure0.05Quantile16052017_coupon_frequency_maturity_test.csv'
# Exposure0.05Quantile16052017_coupon_frequency_maturity.csv
# ExposureData05052017maturities6Test
# ExposureData05052017maturities6
# ExpPosExpo_manyParameters-JavaExport_clean.csv
# ExpPosExpo_manyParameters-JavaExport_clean.csv
# ExposureData05052017SmallTest.csv
# ExposureData11052017_coupon_frequency_maturity.csv    

X_data_all_rand, Y_lable_param1, Y_lable_param2 = loadDataFromCSV(file1Name, True, maturityStyle, True)
OtherTestData_rand, OtherTestLables_rand_param1, OtherTestLables_rand_param2 = loadDataFromCSV(file2Name, True, maturityStyle, True)

# Stack Data together
# X_data_all_rand = np.row_stack((X_data_all_rand, OtherTestData_rand))
# Y_lable_all_rand = np.row_stack((Y_lable_all_rand, OtherTestLables_rand))

# separate data in test & training
# test_length = 250
test_length = int(len(X_data_all_rand) * 0.1) # ...% test data
train_length = len(X_data_all_rand) - test_length
X_data_train = np.float32(X_data_all_rand[0: train_length])
X_data_test = np.float32(X_data_all_rand[train_length : len(X_data_all_rand)])
X_lables_train_param1 = np.float32(Y_lable_param1[0: train_length])
X_lables_test_param1 = np.float32(Y_lable_param1[train_length : len(X_data_all_rand)])
X_lables_train_param2 = np.float32(Y_lable_param2[0: train_length])
X_lables_test_param2 = np.float32(Y_lable_param2[train_length : len(X_data_all_rand)])
print('Data separated')    

# tf Graph input
x = tf.placeholder(tf.float32, [None, n_input])
y_param1 = tf.placeholder(tf.float32, [None, n_classes_param1])
y_param2 = tf.placeholder(tf.float32, [None, n_classes_param2])
keep_prob = tf.placeholder(tf.float32) # dropout (keep probability)

# Create some wrappers for simplicity
def conv1d(x, W, b, strides=1):
    # Conv2D wrapper, with bias and relu activation
    # see padding explanation here http://stackoverflow.com/questions/37674306/what-is-the-difference-between-same-and-valid-padding-in-tf-nn-max-pool-of-t
    x = tf.nn.conv1d(x, W, stride=strides, padding='SAME')
    x = tf.nn.bias_add(x, b)
    return tf.nn.relu(x)


def maxpool1d(x, k=2):   
    # MaxPool2D wrapper
    return tf.nn.max_pool(x, ksize=[1, k, 1, 1], strides=[1, k, 1, 1],
                          padding='SAME')


# Create model
def conv_net(x, weights, biases, dropout):
    # Reshape input picture
    x = tf.reshape(x, shape=[-1, 120, 1])

    # Convolution Layer
    conv1 = conv1d(x, weights['wc1'], biases['bc1'], strides = 1 )
    
    # Max Pooling (down-sampling)
    conv1 = tf.reshape(conv1, shape=[-1, 120, 1, conv1Feature_Number])
    maxp1 = maxpool1d(conv1, k=2) # k sollte eigentlich 2 sein aber hier keine 2d Daten
#    maxp1 = tf.nn.local_response_normalization(maxp1)
    maxp1 = tf.reshape(maxp1, shape=[-1, 60, conv1Feature_Number])

    # Convolution Layer
    conv2 = conv1d(maxp1, weights['wc2'], biases['bc2'], strides = 1)

    # Max Pooling (down-sampling)
    conv2 = tf.reshape(conv2, shape=[-1, 60, 1, conv2Feature_Number])
#    conv2 = tf.nn.local_response_normalization(conv2)
    maxp2 = maxpool1d(conv2, k=2)
    maxp2 = tf.reshape(maxp2, shape=[-1, 30, conv2Feature_Number]) 
    
    # Fully connected layer 1
    # Reshape maxp2 output to fit fully connected layer input
    fc1 = tf.reshape(maxp2, [-1, weights['wd1'].get_shape().as_list()[0]])
    fc1 = tf.add(tf.matmul(fc1, weights['wd1']), biases['bd1'])
    relu = tf.nn.relu(fc1) # max(features, 0)

    # Fully connected layer 2
    fc2 = tf.add(tf.matmul(relu, weights['wd2']), biases['bd2'])
    relu = tf.nn.relu(fc2) # max(features, 0)    
    
    # Apply Dropout
    drop = tf.nn.dropout(relu, dropout)

    # Output, class prediction
    out = tf.add(tf.matmul(drop, weights['out']), biases['out'])
    return out

# Store layers weight & bias
weights_param1 = {
    # 15x1 conv, 1 input, 32 outputs
    'wc1': tf.Variable(tf.random_normal([conv1Kernal_size, 1, conv1Feature_Number])),
    # 10x1 conv, 32 inputs, 64 outputs
    'wc2': tf.Variable(tf.random_normal([conv2Kernal_size, conv1Feature_Number, conv2Feature_Number])),
    # fully connected,30*1*64 inputs, 1024 outputs
    'wd1': tf.Variable(tf.random_normal([30*1*conv2Feature_Number, 1024])),
    # fully connected, 1024 inputs, 512 outputs        
    'wd2': tf.Variable(tf.random_normal([1024, 512])),
    # 1024 inputs, 10 outputs (class prediction)
    'out': tf.Variable(tf.random_normal([512, n_classes_param1]))
}
weights_param2 = {
    # 15x1 conv, 1 input, 32 outputs
    'wc1': tf.Variable(tf.random_normal([conv1Kernal_size, 1, conv1Feature_Number])),
    # 10x1 conv, 32 inputs, 64 outputs
    'wc2': tf.Variable(tf.random_normal([conv2Kernal_size, conv1Feature_Number, conv2Feature_Number])),
    # fully connected,30*1*64 inputs, 1024 outputs
    'wd1': tf.Variable(tf.random_normal([30*1*conv2Feature_Number, 1024])),
    # fully connected, 1024 inputs, 512 outputs        
    'wd2': tf.Variable(tf.random_normal([1024, 512])),
    # 1024 inputs, 10 outputs (class prediction)
    'out': tf.Variable(tf.random_normal([512, n_classes_param2]))
}
"""
savedWeights = {
    'wc1': np.zeros((conv1Kernal_size, 1, conv1Feature_Number)),
    'wc2': np.zeros((conv2Kernal_size, conv1Feature_Number, conv2Feature_Number)),
    'wd1': np.zeros((120*1*conv2Feature_Number, 1024)),
    'wd2': np.zeros((1024, 512)),
    'out': np.zeros((1024, n_classes))
}
"""
biases_param1 = {
    'bc1': tf.Variable(tf.random_normal([conv1Feature_Number])),
    'bc2': tf.Variable(tf.random_normal([conv2Feature_Number])),
    'bd1': tf.Variable(tf.random_normal([1024])),
    'bd2': tf.Variable(tf.random_normal([512])),
    'out': tf.Variable(tf.random_normal([n_classes_param1]))
}
biases_param2 = {
    'bc1': tf.Variable(tf.random_normal([conv1Feature_Number])),
    'bc2': tf.Variable(tf.random_normal([conv2Feature_Number])),
    'bd1': tf.Variable(tf.random_normal([1024])),
    'bd2': tf.Variable(tf.random_normal([512])),
    'out': tf.Variable(tf.random_normal([n_classes_param2]))
}
"""
savedBiases = {
    'bc1': np.zeros((conv1Feature_Number)),
    'bc2': np.zeros((conv2Feature_Number)),
    'bd1': np.zeros((1024)),
    'bd2': np.zeros((512)),
    'out': np.zeros((n_classes))
}
"""
# Construct model
pred_param1 = conv_net(x, weights_param1, biases_param1, keep_prob) # calculates the probabilities of the different types as array
pred_param2 = conv_net(x, weights_param2, biases_param2, keep_prob) # calculates the probabilities of the different types as array

# scaling to avoid the very big output of matrix multiplications in conv_net
pred_scaled_param1 = pred_param1 / 1000
pred_scaled_param2 = pred_param2 / 1000

# Define loss and optimizer
cost_param1 = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=pred_scaled_param1, labels=y_param1))
cost_param2 = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=pred_scaled_param2, labels=y_param2))
cost = cost_param1 + cost_param2

optimizer = tf.train.AdamOptimizer(learning_rate=learning_rate).minimize(cost)

# Evaluate model
correct_pred_param1 = tf.equal(tf.argmax(pred_scaled_param1, 1), tf.argmax(y_param1, 1)) # argmax gibt die Stelle an der die 1 steht; danach wird verglichen ob sie bei den beiden an der gleichen Stelle ist. Wenn ja --> richtig geschätzt also true sonst false. Also entsthet ein Vector[Booleans]    
correct_pred_param2 = tf.equal(tf.argmax(pred_scaled_param2, 1), tf.argmax(y_param2, 1)) # argmax gibt die Stelle an der die 1 steht; danach wird verglichen ob sie bei den beiden an der gleichen Stelle ist. Wenn ja --> richtig geschätzt also true sonst false. Also entsthet ein Vector[Booleans]    
accuracy_param1 = tf.reduce_mean(tf.cast(correct_pred_param1, tf.float32)) # cast tensor to tf.float32 type and calculates the overall mean -> how many right predictions on average
accuracy_param2 = tf.reduce_mean(tf.cast(correct_pred_param2, tf.float32)) # cast tensor to tf.float32 type and calculates the overall mean -> how many right predictions on average

# Initializing the variables
init = tf.global_variables_initializer()

# take batch
def next_batch(x, batch_size, batch_number):
    return x[ batch_number * batch_size : batch_number * batch_size + batch_size]

# Launch the graph
with tf.Session() as sess:
    sess.run(init)
    print("Network param 1 variables initialized (", conv1Kernal_size*1*conv1Feature_Number + conv2Kernal_size*conv1Feature_Number*conv2Feature_Number + 30*1*conv2Feature_Number*1024 + 1024*512 + 512*n_classes_param1, ")")    
    print("Network param 2 variables initialized (", conv1Kernal_size*1*conv1Feature_Number + conv2Kernal_size*conv1Feature_Number*conv2Feature_Number + 30*1*conv2Feature_Number*1024 + 1024*512 + 512*n_classes_param2, ")")    
    step = 1
    batch_number = 0
    r = 0
    stepsToRunThroughTrainingsData = int(train_length / batch_size)
    print("Start training")
    # Keep training until reach max iterations
    while step * batch_size < training_iters:
        
        # start at the beginning of Trainingsdata after passing it
        if((step - r * stepsToRunThroughTrainingsData) > stepsToRunThroughTrainingsData):
            batch_number = 0
            r += 1
            # new order of rows of data for next trainings run
            X_data_train, X_lables_train_param1, X_lables_train_param2 = randomizeRows(X_data_train, X_lables_train_param1, X_lables_train_param2)
            print('round ', r+1, "   ", step)
        batch_x = next_batch(X_data_train, batch_size, batch_number)
        batch_y_param1 = next_batch(X_lables_train_param1, batch_size, batch_number)
        batch_y_param2 = next_batch(X_lables_train_param2, batch_size, batch_number)
        batch_number += batch_number
        # Run optimization op (backprop)
        sess.run(optimizer, feed_dict={x: batch_x, 
                                       y_param1: batch_y_param1, 
                                       y_param2: batch_y_param2,
                                       keep_prob: dropout})
        if step % display_step == 0:
            # Calculate batch loss and accuracy
            loss_overall, acc_param1, acc_param2 = sess.run([cost, accuracy_param1, accuracy_param2], feed_dict={x: batch_x,
                                                              y_param1: batch_y_param1, 
                                                              y_param2: batch_y_param2,
                                                              keep_prob: 1.})
            print("Iter " + str(step * batch_size) + ", Minibatch Loss= " + \
                  "{:.6f}".format(loss_overall) + ", Training Accuracy param1= " + \
                  "{:.5f}".format(acc_param1) + ", Training Accuracy param2= " + \
                  "{:.5f}".format(acc_param2))
        step += 1
        
        # collect data for TensorBoard
#        with tf.name_scope('cost'):
#            tf.summary.scalar('cost', cost)
#        with tf.name_scope('dropout'):
#            tf.summary.histogram('dropout_keep_probability', keep_prob)
    print("Training Finished!")

    # Calculate accuracy for test data
    TestAtEnd_param1, TestAtEnd_param2 = sess.run([accuracy_param1, accuracy_param2], feed_dict={x: X_data_test,
                                      y_param1: X_lables_test_param1,
                                      y_param2: X_lables_test_param2,
                                      keep_prob: 1.})
    print("Testing Accuracy Parameter 1:", float(TestAtEnd_param1))
    print("Testing Accuracy Parameter 2:", float(TestAtEnd_param2))

    OtherTest_param1, OtherTest_param2 = sess.run([accuracy_param1, accuracy_param2], feed_dict={x: OtherTestData_rand,
                                                    y_param1: OtherTestLables_rand_param1,
                                                    y_param2: OtherTestLables_rand_param2,
                                                    keep_prob: 1.})
    print("Other Testing Accuracy Parameter 1:", float(OtherTest_param1))
    print("Other Testing Accuracy Parameter 2:", float(OtherTest_param2))

    # merge and store the summary
#    merged = tf.summary.merge_all()
#    train_writer = tf.summary.FileWriter('summaryData', sess.graph)
    
# save the run in dict
newEntry = {"test_accuracy_param1" : TestAtEnd_param1,
            "test_accuracy_param2" : TestAtEnd_param2,
            "learning_rate" : learning_rate,
            "training_iters" : training_iters,
            "conv1Kernal_size" : conv1Kernal_size,
            "conv2Kernal_size" : conv2Kernal_size,
            "dropout" : dropout,
            "conv1Feature_Number" : conv1Feature_Number,
            "conv2Feature_Number" : conv2Feature_Number,
            "OtherTest_Accuracy param1" : OtherTest_param1,
            "OtherTest_Accuracy param2" : OtherTest_param2,
            "n_classes param1" : n_classes_param1,
            "n_classes param2" : n_classes_param2,
            "train_length" : train_length,
            "batch_size" : batch_size,
            "comment" : 'Train two networks at same time for two swap parameters'}  
results_two_param.append(newEntry)


  
#%%
# print results
for k, entry in enumerate(results):
    if(k>0):
        print("Accuracy ", entry["test_accuracy"])

#%%

def predictData(CSV_Name, maturityStyle, randomize):

    fileName_External = CSV_Name
    externalTestDataPoints, externalTestLables = loadDataFromCSV(fileName_External, True, maturityStyle, randomize)
    
    # maturityStyle = 'only 6' # 'normal': 15 classes; other: 'only 6'
    
    if(maturityStyle == 'only 6'):
        n_classes = 6
    else: 
        n_classes = 15
    
    # tf Graph input
    x = tf.placeholder(tf.float32, [None, n_input])
    y = tf.placeholder(tf.float32, [None, n_classes])
    keep_prob = tf.placeholder(tf.float32) # dropout (keep probability)
    
    # restore layers weight & bias
    weights_External = {
        'wc1': tf.Variable(savedWeights['wc1']),
        'wc2': tf.Variable(savedWeights['wc2']),
        'wd1': tf.Variable(savedWeights['wd1']),
        'wd2': tf.Variable(savedWeights['wd2']),
        'out': tf.Variable(savedWeights['out'])}
    biases_External = {
        'bc1': tf.Variable(savedBiases['bc1']),
        'bc2': tf.Variable(savedBiases['bc2']),
        'bd1': tf.Variable(savedBiases['bd1']),
        'bd2': tf.Variable(savedBiases['bd2']),
        'out': tf.Variable(savedBiases['out'])}
    print('weights loaded')
    
    # Construct model
    pred_External = conv_net(x, weights_External, biases_External, keep_prob) # calculates the probabilities of the different types as array
    # scaling
    pred_External_scaled = pred_External / 10000

    # Evaluate model
    correct_pred_External = tf.equal(tf.argmax(pred_External_scaled, 1), tf.argmax(y, 1)) # argmax gibt die Stelle an der die 1 steht; danach wird verglichen ob sie bei den beiden an der gleichen Stelle ist. Wenn ja --> richtig geschätzt also true sonst false. Also entsthet ein Vector[Booleans]    
    accuracy_External = tf.reduce_mean(tf.cast(correct_pred_External, tf.float32)) # cast tensor to tf.float32 type and calculates the overall mean -> how many right predictions on average
    
    # Initializing the variables
    init_External = tf.global_variables_initializer()
    
    # Launch the graph
    with tf.Session() as sess:
        sess.run(init_External)
        print('Network initialized')
        externalTest, pred_External_Vector = sess.run([accuracy_External, pred_External_scaled], feed_dict={x: externalTestDataPoints,
                                                        y: externalTestLables,
                                                        keep_prob: 1.})
        print("External Accuracy:", float(externalTest))
        
    return pred_External_Vector
            
CSV_Name = '/Users/Chris/Python/Machine Learning/Masterarbeit1/ExposureData11052017_coupon_frequency_maturity-test.csv'
maturityStyle = 'normal'
predictedProbabilities_scaled_logits = predictData(CSV_Name, maturityStyle, True)
print(predictedProbabilities_scaled_logits)
#%%
with tf.Session() as sess:
    predictedProbabilities_softmax = tf.nn.softmax(predictedProbabilities_scaled_logits).eval()
    print('done')
#    print(predictedProbabilities_softmax)

#%%
