#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jul  2 15:46:28 2017

@author: Chris

here I use cleaned and randomized data from "clean-randomize-data.py"
The code calculates 16 features and saves them als csv.

"""
import numpy as np
import pandas as pd
from useTrainedModel_fct import useTrainedModel

def calculateFeaturesANDProbsFromTrainedModel(fileName_clean_randomized, fileName_features):
    #fileName =                      '/Users/Chris/Python/Machine Learning/Masterarbeit1/all Data/Data from CIP/Exposure_0.05Quantile_04062017 zusammengesetzt-unvollständig-clean.csv'
#    fileName_clean_randomized =     '/Users/Chris/Python/Machine Learning/Masterarbeit1/all Data/Data from CIP/Exposure_0.05Quantile_04062017 zusammengesetzt-unvollständig-clean-rand.csv'
#    fileName_features =             '/Users/Chris/Python/Machine Learning/Masterarbeit1/all Data/Data from CIP/Exposure_0.05Quantile_04062017 zusammengesetzt-unvollständig-clean-rand-features.csv'
    
    completeData = pd.read_csv(fileName_clean_randomized, header=None, sep=";")
    data =      completeData.iloc[:, : completeData.shape[1] - 10 ].values
    lables =    completeData.iloc[:, completeData.shape[1] - 10 : ].values
    print("data loaded")
    
    # clean und randomized ausgelagert, d.h. ich nehme an das wurde schon erledigt und wir laden diese aus csv
    
    
    timeSeriesLength = 360
    numberOfProfiles = data.shape[0]
    
    #def featureCalculator_np(data, timeSeriesLength, numberOfProfiles):
    ## Feature 1 & 2: Maximum & Position of the maximum
    print("calclate features 1 & 2")
    maximum = np.zeros(numberOfProfiles, dtype = np.float32)
    maximumPosition = np.zeros(numberOfProfiles, dtype = np.float32)
    for i in range(0, numberOfProfiles):   #Loop over the input serieses
        maximum[i] = max(data[i])
        negmaximum = max(-data[i])
        if(negmaximum > maximum[i]): 
            maximum[i] = negmaximum
            maximumPosition[i] = np.argmax(-data[i])
        else:
            maximumPosition[i] = np.argmax(data[i])
            
    ## Feature 3: First Point
    print("calclate features 3")
    entryPoint = data[:,0]
    
    ## Feature 4: Delta(maximum, first point)
    print("calclate features 4")
    deltaMaxFist = maximum - entryPoint
    
    ## Feature 5: neg delta to the next point (first derivative)
    print("calclate features 5")
    delta = np.diff(-data, n=1, axis=1)
    
    ## Feature 6: max(delta, 0) = down jumps
    print("calclate features 6")
    jumps = np.maximum(delta,0)        
            
    ## Feature 7: time passed after last jump
    print("calclate features 7")
    timeAfterJump = np.zeros((numberOfProfiles, 359), dtype = np.float32)
    for i in range(0, numberOfProfiles):   #Loop over the input serieses    
        time = 0
        for j in range(0, timeSeriesLength - 1):
            if(jumps[i,j] == 0): time = time +1
            if(jumps[i,j] > 0): time = 0
            timeAfterJump[i,j] = time
    
    ## Feature 8: number of zeros at the end (length of the zero line at the end)
    print("calclate features 8")
    numberOfZeros = np.zeros(numberOfProfiles, dtype = np.float32)
    for i in range(numberOfProfiles):   #Loop over the input serieses    
        for k in range(timeSeriesLength-1,-1,-1):
            if data[i,k] == 0: numberOfZeros[i] += 1
    
    ## Feature 9: maximal distance to the next drop3
    print("calclate features 9")
    maximalDistanceToTheNextDrop = np.zeros(numberOfProfiles, dtype = np.float32)
    for i in range(0, numberOfProfiles):   #Loop over the input serieses   
        maximalDistanceToTheNextDrop[i] = max(timeAfterJump[i,int(maximumPosition[i]):int(360-numberOfZeros[i])])
    
        
    ## Feature 10: mean of the tensor without last zeros
    print("calclate features 10")
    mean = np.mean(data, axis = 1)
        
    ## Feature 11: variance of the tensor without last zeros
    print("calclate features 11")
    variance = np.var(data, axis = 1)  
    
    ## Feature 12 & 13: number of jumps and average jump higth
    print("calclate features 12 & 13")
    numberOfJumps = np.zeros(numberOfProfiles, dtype = np.float32)
    averageJump = np.zeros(numberOfProfiles, dtype = np.float32)
    for i in range(0, numberOfProfiles):   #Loop over the input serieses    
        numberOfJumps[i] = (jumps[i] > 0).sum()
        if [jump for jump in jumps[i] if jump > 0] != []:
            averageJump[i] = np.mean([jump for jump in jumps[i] if jump > 0])
        else:
            averageJump[i] = 0        
    
    ## Feature 14: number of jumps relative to net (real) time series length
    print("calclate features 14")
    numberOfJumpsRelativeToLength = numberOfJumps / (360-numberOfZeros)
    
    ## Feature 15: highest jump
    print("calclate features 15")
    maximalJump = np.max(jumps, axis = 1)
    
    ## Feature 16: curvature (second derivative)
    print("calclate features 16")
    curvature = np.diff(delta, n=1, axis=1)
            
    print("Features calculated")
    
    ### use trained Models to calculate probs        
    numberOfNeuronsInFirstLayers_4TrainedModels = 200
    n_classes_maturity = 4
    n_classes_frequency = 3
    n_classes_coupon = 6
    
    networkInput_trainedModels = [maximum, maximumPosition, entryPoint, numberOfZeros, mean, variance, maximalDistanceToTheNextDrop, deltaMaxFist, numberOfJumpsRelativeToLength, maximalJump, jumps]
    name_SavesModel = 'ownFeatureExtraction_MultiDimInput_Maturity.ckpt'
    probabilities_Maturity = useTrainedModel(networkInput_trainedModels, name_SavesModel, n_classes_maturity, numberOfNeuronsInFirstLayers_4TrainedModels)
    name_SavesModel = 'ownFeatureExtraction_MultiDimInput_Frequency.ckpt'
    probabilities_Frequency = useTrainedModel(networkInput_trainedModels, name_SavesModel, n_classes_frequency, numberOfNeuronsInFirstLayers_4TrainedModels)
    name_SavesModel = 'ownFeatureExtraction_MultiDimInput_Coupon.ckpt'
    probabilities_Coupon = useTrainedModel(networkInput_trainedModels, name_SavesModel, n_classes_coupon, numberOfNeuronsInFirstLayers_4TrainedModels)
    
    # save all features, lables and probs
    concat = np.column_stack((maximum, maximumPosition, entryPoint, deltaMaxFist, delta, jumps, timeAfterJump, numberOfZeros, maximalDistanceToTheNextDrop, mean, variance, numberOfJumps, averageJump, numberOfJumpsRelativeToLength, maximalJump, curvature, probabilities_Maturity, probabilities_Frequency, probabilities_Coupon, lables))
    print("data stacked together") # inklisive lables
    
    df = pd.DataFrame(concat)
    df.to_csv(fileName_features, header=None, sep=";", index = False, index_label = False)
    print("data saved")
    
    
    
    
    
    
    
    """
    completeData = pd.read_csv(fileName_features, header=None, sep=";")
    concat_loaded = completeData.iloc[:,:].values
    print("data loaded")
    
    maximum2                         = concat_loaded[:,0]
    maximumPosition2                 = concat_loaded[:,1]
    entryPoint2                      = concat_loaded[:,2]
    deltaMaxFist2                    = concat_loaded[:,3]
    delta2                           = concat_loaded[:,4:363]
    jumps2                           = concat_loaded[:,363:722]
    timeAfterJump2                   = concat_loaded[:,722:1081]
    numberOfZeros2                   = concat_loaded[:,1081]
    maximalDistanceToTheNextDrop2    = concat_loaded[:,1082]
    mean2                            = concat_loaded[:,1083]
    variance2                        = concat_loaded[:,1084]
    numberOfJumps2                   = concat_loaded[:,1085]
    averageJump2                     = concat_loaded[:,1086]
    numberOfJumpsRelativeToLength2   = concat_loaded[:,1087]
    maximalJump2                     = concat_loaded[:,1088]
    curvature2                       = concat_loaded[:,1089:1447]
    probabilities_Maturity2          = concat_loaded[:,1447:1451]
    probabilities_Frequency2         = concat_loaded[:,1451:1454]
    probabilities_Coupon2            = concat_loaded[:,1454:1460]
    lables2                          = concat_loaded[:,1460:1470]
    print("data separated")
    """