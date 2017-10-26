# -*- coding: utf-8 -*-
"""
Spyder Editor
#
This is a temporary script file.
"""
#%%
import os
import numpy as np


#file Path for functions
#funcPath = 'C:/Users/ellio/OneDrive/Documents/GitHub/ML-for-Chinese-Calligraphy/'
funcPath = 'C:\\Users\\Sebastian\\Desktop\\GitHub\\ML-for-Chinese-Calligraphy'
os.chdir(funcPath)
from classFileFunctions import fileFunc as fF

#file path for data
#dataPath = 'C:/Users/ellio/Desktop/training data/iterate test/'
dataPath = 'C:\\Users\\Sebastian\\Desktop\\MLChinese\\CASIA\\HWDtest2\\HWDB1.1tst_gnt'

dataForSaving=0;
data=0;
#get info on gnt file
data,tot = fF.iterateOverFiles(dataPath)
dataInfo = fF.infoGNT(data,tot)
dataForSaving = fF.arraysFromGNT(data,dataInfo)

data=0;#delete data in raw byte form 
fF.saveNPZ(dataPath,"1001to1004",saveLabels=dataForSaving[0],saveImages=dataForSaving[5])

"""Look at the characters in the data"""
characters = dataForSaving[0]
numChars = len(list(set(characters)))
print(list(set(np.sort(characters))))

#try out the 1hot vector method
characters = [ord(i) for i in characters]
b = np.zeros((len(characters), max(characters)+1))
b[np.arange(len(characters)), characters] = 1
