#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May  4 11:42:39 2017

@author: Chris

A Convolutional Network implementation using TensorFlow library.
"""

# first define results, but only one time. Than all the results are archived there
# results=[{}]
#%%

def randomizeRows(VectData, VectLabel):
    # brings the rows of both vectors in the same new random order
    # both vectors need same length
    indices = np.random.permutation(len(VectData))
    tempData = [VectData[i] for i in indices]
    tempLabel = [VectLabel[i] for i in indices]
    return tempData, tempLabel
    
def loadDataFromCSV(path, normalize, randomize): # normalize = True --> normalization over altitude of every row (=time series)
    # Import other test data
    completeData = pd.read_csv(path, header=None, sep=";")
    datapoints = completeData.iloc[:, : completeData.shape[1] - 6 ].values
    lables = completeData.iloc[:, completeData.shape[1] - 3 : completeData.shape[1] - 2 ].values

    # transform the maturity text into integers 
#    for i, text in enumerate(lables):
#        if text == 'QUARTERLY':
#            lables[i] = 0            
#        if text == 'SEMIANNUAL':
#            lables[i] = 1            
#        if text == 'ANNUAL':
#            lables[i] = 2            

    # maturities labels have be of the form 1, 2, ...
    a = np.zeros((datapoints.shape[0], n_classes)) 
    for i, number in enumerate(lables):
        a[i][ int(number[0]) ] = 1        

    lables_Matrix = a
    
    if normalize == True:
        for i in range(0, datapoints.shape[0]):
            # also normalize negative values!!
            maximum = max( np.ndarray.max(datapoints[i]), -np.ndarray.min(datapoints[i]))
            for j in range(0, datapoints.shape[1]):
                datapoints[i][j] = (datapoints[i][j] / maximum)

    # randomize order
    if randomize == True:
        datapoints_rand_list, lables_rand_list = randomizeRows(datapoints, lables_Matrix)
        datapoints_rand = np.float32(datapoints_rand_list)
        lables_rand = np.float32(lables_rand_list)
    else: 
        datapoints_rand = np.float32(datapoints)
        lables_rand = np.float32(lables_Matrix)
    print('Data loaded')
    return datapoints_rand, lables_rand
    
def Model():
    # tf Graph input
    x = tf.placeholder(tf.float32, [None, timeSeriesLength])
    y = tf.placeholder(tf.float32, [None, n_classes])
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
        x = tf.reshape(x, shape=[-1, timeSeriesLength, 1])
    
        # Convolution Layer
        conv1 = conv1d(x, weights['wc1'], biases['bc1'], strides = 1 )
        
        # Max Pooling (down-sampling)
        conv1 = tf.reshape(conv1, shape=[-1, timeSeriesLength, 1, conv1Feature_Number])
        maxp1 = maxpool1d(conv1, k=2) # k sollte eigentlich 2 sein aber hier keine 2d Daten
    #    maxp1 = tf.nn.local_response_normalization(maxp1)
        maxp1 = tf.reshape(maxp1, shape=[-1, int(timeSeriesLength/2), conv1Feature_Number])
    
        # Convolution Layer
        conv2 = conv1d(maxp1, weights['wc2'], biases['bc2'], strides = 1)
    
        # Max Pooling (down-sampling)
        conv2 = tf.reshape(conv2, shape=[-1, int(timeSeriesLength/2), 1, conv2Feature_Number])
    #    conv2 = tf.nn.local_response_normalization(conv2)
        maxp2 = maxpool1d(conv2, k=2)
        maxp2 = tf.reshape(maxp2, shape=[-1, int(timeSeriesLength/4), conv2Feature_Number]) 
        
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
    
    initialValues_wc1_Rauschen = np.random.normal(0,10,[conv1Kernal_size, 1, conv1Feature_Number])
    initialValues_wc1_values = np.zeros([conv1Kernal_size, 1, conv1Feature_Number], dtype = np.float32)
    initialValues_wc1 = np.add(initialValues_wc1_values, initialValues_wc1_Rauschen, dtype = np.float32)

# einzelne kurze Ausschläge
    for i in range(0, 10):
        for run in range(0, int(conv1Kernal_size/3)):
            if initialValues_wc1[(3*run),:,i] > 0:
                initialValues_wc1[(3*run),:,i] = initialValues_wc1[(3*run),:,i] * 5
            else:    
                initialValues_wc1[(3*run),:,i] = initialValues_wc1[(3*run),:,i] * 5

    for i in range(10, 20):
        for run in range(0, int(conv1Kernal_size/6)):
            if initialValues_wc1[(6*run),:,i] > 0:
                initialValues_wc1[(6*run),:,i] = initialValues_wc1[(6*run),:,i] * 5
            else:    
                initialValues_wc1[(6*run),:,i] = initialValues_wc1[(6*run),:,i] * 5

    for i in range(20, 32):
        for run in range(0, int(conv1Kernal_size/12)):
            if initialValues_wc1[(12*run),:,i] > 0:
                initialValues_wc1[(12*run),:,i] = initialValues_wc1[(6*run),:,i] * 5
            else:    
                initialValues_wc1[(12*run),:,i] = initialValues_wc1[(6*run),:,i] * 5

# null ab bestimmten Eintrag
#    for i in range(0, min(conv1Feature_Number, conv1Kernal_size)):
#        for run in range(i, conv1Kernal_size):
#            initialValues_wc1[(run*4):,:,i] = 0
    # print(initialValues_wc1)

# normal 
    # initialValues_wc1 = tf.random_normal([conv1Kernal_size, 1, conv1Feature_Number])
    
    weights = {
        # 15x1 conv, 1 input, 32 outputs
        'wc1': tf.Variable(initialValues_wc1),
        # 10x1 conv, 32 inputs, 64 outputs
        'wc2': tf.Variable(tf.random_normal([conv2Kernal_size, conv1Feature_Number, conv2Feature_Number])),
        # fully connected,30*1*64 inputs, 1024 outputs
        'wd1': tf.Variable(tf.random_normal([int(timeSeriesLength/4)*1*conv2Feature_Number, 1024])),
        # fully connected, 1024 inputs, 512 outputs        
        'wd2': tf.Variable(tf.random_normal([1024, 512])),
        # 1024 inputs, 10 outputs (class prediction)
        'out': tf.Variable(tf.random_normal([512, n_classes]))
    }
    
    savedWeights = {
        'wc1': np.zeros((conv1Kernal_size, 1, conv1Feature_Number)),
        'wc2': np.zeros((conv2Kernal_size, conv1Feature_Number, conv2Feature_Number)),
        'wd1': np.zeros((timeSeriesLength*1*conv2Feature_Number, 1024)),
        'wd2': np.zeros((1024, 512)),
        'out': np.zeros((1024, n_classes))
    }
    
    biases = {
        'bc1': tf.Variable(tf.random_normal([conv1Feature_Number])),
        'bc2': tf.Variable(tf.random_normal([conv2Feature_Number])),
        'bd1': tf.Variable(tf.random_normal([1024])),
        'bd2': tf.Variable(tf.random_normal([512])),
        'out': tf.Variable(tf.random_normal([n_classes]))
    }
    
    savedBiases = {
        'bc1': np.zeros((conv1Feature_Number)),
        'bc2': np.zeros((conv2Feature_Number)),
        'bd1': np.zeros((1024)),
        'bd2': np.zeros((512)),
        'out': np.zeros((n_classes))
    }
    # Construct model
    pred = conv_net(x, weights, biases, keep_prob) # calculates the probabilities of the different types as array
    # scaling to avoid the very big output of matrix multiplications in conv_net
    pred_scaled = pred / 1000
    # Define loss and optimizer
    cost = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=pred_scaled, labels=y))
    
    optimizer = tf.train.AdamOptimizer(learning_rate=learning_rate).minimize(cost)
    
    # Evaluate model
    correct_pred = tf.equal(tf.argmax(pred_scaled, 1), tf.argmax(y, 1)) # argmax gibt die Stelle an der die 1 steht; danach wird verglichen ob sie bei den beiden an der gleichen Stelle ist. Wenn ja --> richtig geschätzt also true sonst false. Also entsthet ein Vector[Booleans]    
    accuracy = tf.reduce_mean(tf.cast(correct_pred, tf.float32)) # cast tensor to tf.float32 type and calculates the overall mean -> how many right predictions on average
    
    # Initializing the variables
    init = tf.global_variables_initializer()

    return init, optimizer, cost, accuracy, x, y, weights, savedWeights, biases, savedBiases, keep_prob, pred, initialValues_wc1
    
#%%

import tensorflow as tf
import pandas as pd
import numpy as np

tf.reset_default_graph()

# Parameters
learning_rate = 0.001
training_iters = 4000
batch_size = 128
display_step = 8

# Network Parameters
dropout = 0.75 # Dropout, probability to keep units
conv1Kernal_size = 120
conv1Feature_Number = 32
conv2Kernal_size = 40
conv2Feature_Number = 64

timeSeriesLength = 360  # time series data input shape: 120 data points
n_classes = 3


file1Name = '/Users/Chris/Python/Machine Learning/Masterarbeit1/Exposure_0.05Quantile_22052017.csv'
file2Name = '/Users/Chris/Python/Machine Learning/Masterarbeit1/Exposure_0.05Quantile_22052017.csv'
# Exposure0.05Quantile16052017_coupon_frequency_maturity.csv
# Exposure0.05Quantile16052017_coupon_frequency_maturity_test.csv
# ExposureData05052017maturities6Test
# ExposureData05052017maturities6
# ExpPosExpo_manyParameters-JavaExport_clean.csv
# ExpPosExpo_manyParameters-JavaExport_clean.csv
# ExposureData05052017SmallTest.csv
# ExposureData11052017_coupon_frequency_maturity.csv    

X_data_all_rand, Y_lable_all_rand = loadDataFromCSV(file1Name, False, True)
OtherTestData_rand, OtherTestLables_rand = loadDataFromCSV(file2Name, False, False)

# Stack Data together
# X_data_all_rand = np.row_stack((X_data_all_rand, OtherTestData_rand))
# Y_lable_all_rand = np.row_stack((Y_lable_all_rand, OtherTestLables_rand))

# separate data in test & training
# test_length = 250
test_length = int(len(X_data_all_rand) * 0.1) # ...% test data
train_length = len(X_data_all_rand) - test_length
X_data_train = np.float32(X_data_all_rand[0: train_length])
X_data_test = np.float32(X_data_all_rand[train_length : len(X_data_all_rand)])
X_lables_train = np.float32(Y_lable_all_rand[0: train_length])
X_lables_test = np.float32(Y_lable_all_rand[train_length : len(X_data_all_rand)])
print('Data separated')    

init, optimizer, cost, accuracy, x, y, weights, savedWeights, biases, savedBiases, keep_prob, pred, initialValues_wc1 = Model()

# take batch
def next_batch(x, batch_size, batch_number):
    return x[ batch_number * batch_size : batch_number * batch_size + batch_size]

CSV_Name = '/Users/Chris/Python/Machine Learning/Masterarbeit1/Exposure_0.05Quantile_22052017.csv'

X, Y = loadDataFromCSV(CSV_Name, False, False)

# Launch the graph
with tf.Session() as sess:
    sess.run(init)
    print("Network variables initialized (", conv1Kernal_size*1*conv1Feature_Number + conv2Kernal_size*conv1Feature_Number*conv2Feature_Number + 30*1*conv2Feature_Number*1024 + 1024*512 + 512*n_classes, ")")    
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
            randomizeRows(X_data_train, X_lables_train)
            print('round ', r+1, "   ", step)
        batch_x = next_batch(X_data_train, batch_size, batch_number)
        batch_y = next_batch(X_lables_train, batch_size, batch_number)
        batch_number += batch_number
        # Run optimization op (backprop)
        sess.run(optimizer, feed_dict={x: batch_x, y: batch_y,
                                       keep_prob: dropout})
        if step % display_step == 0:
            # Calculate batch loss and accuracy
            loss, acc = sess.run([cost, accuracy], feed_dict={x: batch_x,
                                                              y: batch_y,
                                                              keep_prob: 1.})
            print("Iter " + str(step * batch_size) + ", Minibatch Loss= " + \
                  "{:.6f}".format(loss) + ", Training Accuracy= " + \
                  "{:.5f}".format(acc))
        step += 1
        
        # collect data for TensorBoard
#        with tf.name_scope('cost'):
#            tf.summary.scalar('cost', cost)
#        with tf.name_scope('dropout'):
#            tf.summary.histogram('dropout_keep_probability', keep_prob)

        if(step * batch_size >= training_iters - batch_size):
            savedWeights['wc1'] = weights['wc1'].eval()
            savedWeights['wc2'] = weights['wc2'].eval()
            savedWeights['wd1'] = weights['wd1'].eval()
            savedWeights['wd2'] = weights['wd2'].eval()
            savedWeights['out'] = weights['out'].eval()
            savedBiases['bc1'] = biases['bc1'].eval()
            savedBiases['bc2'] = biases['bc2'].eval()
            savedBiases['bd1'] = biases['bd1'].eval()
            savedBiases['bd2'] = biases['bd2'].eval()
            savedBiases['out'] = biases['out'].eval()
            print("Weights saved")            
            
            saver = tf.train.Saver()
            save_path = saver.save(sess, "/Users/Chris/Python/Machine Learning/Masterarbeit1/CNN/savedModels/CNN-360-Model-3.ckpt")
        
    print("Model saved in file: %s" % save_path)

            
    print("Training Finished!")
    
    # Calculate accuracy for test data
    TestAtEnd = float(sess.run(accuracy, feed_dict={x: X_data_test,
                                      y: X_lables_test,
                                      keep_prob: 1.}))
    print("Testing Accuracy:", TestAtEnd)

    OtherTest = float(sess.run(accuracy, feed_dict={x: OtherTestData_rand,
                                                    y: OtherTestLables_rand,
                                                    keep_prob: 1.}))
    print("Other Testing Accuracy:", OtherTest)   

# save the run in dict
newEntry = {"test_accuracy" : TestAtEnd,
            "learning_rate" : learning_rate,
            "training_iters" : training_iters,
            "conv1Kernal_size" : conv1Kernal_size,
            "conv2Kernal_size" : conv2Kernal_size,
            "dropout" : dropout,
            "conv1Feature_Number" : conv1Feature_Number,
            "conv2Feature_Number" : conv2Feature_Number,
            "OtherTest_Accuracy" : OtherTest,
            "n_classes" : n_classes,
            "train_length" : train_length,
            "batch_size" : batch_size,
            "comment" : 'coupon without normalization'}  
results.append(newEntry)
  
#%%

tf.reset_default_graph()

CSV_Name = '/Users/Chris/Python/Machine Learning/Masterarbeit1/Exposure_0.05Quantile_22052017.csv'

X, Y = loadDataFromCSV(CSV_Name, False, False)

init, optimizer, cost, accuracy, x, y, weights, savedWeights2, biases, savedBiases2, keep_prob, pred, q = Model()

# Launch the graph
with tf.Session() as sess:
    sess.run(init)    
    saver = tf.train.Saver()
    saver.restore(sess, "/Users/Chris/Python/Machine Learning/Masterarbeit1/CNN/savedModels/CNN-360-Model-3.ckpt"   )
    print("Session restored.")    
    test, logits = sess.run([accuracy, pred], feed_dict={   x: X, 
                                            y: Y,
                                            keep_prob: 1.})
    print("External Test Accuracy:", float(test))   
    logits_scaled = logits / 100000 # das scaling an dieser Stelle verändert die Wkeiten stark, aber nicht die Reihenfolge
    probabilities = tf.nn.softmax(logits_scaled).eval()

# import pandas as pd 
# df = pd.DataFrame(probabilities)
# df.to_csv('/Users/Chris/Python/Machine Learning/Masterarbeit1/Exposure_0.05Quantile_22052017_evaluated.csv')
# ar = np.asarray(probabilities)
# ar.tofile('/Users/Chris/Python/Machine Learning/Masterarbeit1/Exposure_0.05Quantile_22052017_evaluated.csv',sep=';',format='%10.5f')

# Stack infos together
probabilities_argmax = np.argmax(probabilities, 1)
Y_argmax = np.argmax(Y, 1)
toBePrinted = np.column_stack((Y_argmax, probabilities_argmax, probabilities))

# print the probabilities into a xlsx
import xlsxwriter
workbook = xlsxwriter.Workbook('/Users/Chris/Python/Machine Learning/Masterarbeit1/Exposure_0.05Quantile_24052017_evaluated.xlsx')
worksheet = workbook.add_worksheet('Results Analysis')
row = 0
for col, data in enumerate(np.transpose(toBePrinted)):
    worksheet.write_column(row, col, data)
    
worksheet = workbook.add_worksheet('Weights Analysis')
row = 0
for col, data in enumerate(np.concatenate(savedWeights['wc1']).astype(None)):
    worksheet.write_column(row, col, data)

workbook.close()

#%%