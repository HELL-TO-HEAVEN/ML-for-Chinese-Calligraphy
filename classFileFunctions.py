# -*- coding: utf-8 -*-
"""
Created on Thu Oct 12 16:50:06 2017

@author: Sebastian
"""

import os
import numpy as np
from classImageFunctions import imageFunc as iF
from collections import namedtuple

class fileFunc(object):

    """Class of functions that perform on files"""
    def byteToInt(byte,byteOrder='little'):
        return int.from_bytes(byte, byteorder=byteOrder)
    
    #Function that reads the NPZ file 'name' at 'path' and returns the file object
    def readNPZ(path,name,labelName,imageName):
        fullName = f"{path}{name}"
        with open(fullName, 'rb') as ifs:
            fileNPZ = np.load(ifs)
            return fileNPZ[labelName],fileNPZ[imageName]
        
    #function that saves a list of arrays 'namedArrays' to the file 'name' at
    #location 'path' with the option of compression 'compressed'      
    def saveNPZ(path,name,compressed=False,**namedArrays):
        fullName = f"{path}{name}"
        with open(fullName, 'wb') as ofs:
            if compressed:
                np.savez_compressed(ofs,**namedArrays)
            else:
                np.savez(ofs,**namedArrays)
        ofs.close();
    
    def arraysFromGNT(path,name,info):
        os.chdir(path)
        with open(name, 'rb') as f:
            fullFile = f.readlines()[0];
        f.close();
        #create arrays to store data read in
        character = np.zeros(info.numSamples,np.unicode);
        images = np.zeros((info.numSamples,info.maxWidth*info.maxHeight))
        #place data into arrays
        position = 0;
        for i in range(0,info.numSamples-1):
            sampleSize = fileFunc.byteToInt(fullFile[position:position+4]);
            character[i] = fullFile[position+4:position+6].decode('gb2312');
            width = fileFunc.byteToInt(fullFile[position+6:position+8]);
            height = fileFunc.byteToInt(fullFile[position+8:position+10]);
            image = np.zeros((height,width))
            for j in range(0,height):
                for k in range(0,width):
                    image[j][k]=fullFile[position+10+j*width+k];
            position +=sampleSize;
            print(i)
            print('character',character[i])
            im = iF.arrayToImage(image,height,width)
            imResize=iF.resizeImage(im,info.maxWidth,info.maxHeight)
            images[i] = iF.PIL2array(imResize);
        return [character,images,info.maxHeight,info.maxWidth]
    
    def arraysFromGNT2(fullFile,info):
        #create arrays to store data read in
        totalSamples = int(np.sum(info.numSamples));
        characters = np.zeros(totalSamples,np.unicode);
        images = np.zeros((totalSamples,info.maxWidth*info.maxHeight))
        #place data into arrays
        k=0
        for j in range(len(info.numSamples)):
            position = 0;
            for i in range(int(info.numSamples[j])):
                sampleSize = fileFunc.byteToInt(fullFile[j][position:position+4]);
                characters[k] = fullFile[j][position+4:position+6].decode('gb2312');
                width = fileFunc.byteToInt(fullFile[j][position+6:position+8]);
                height = fileFunc.byteToInt(fullFile[j][position+8:position+10]);
                image = np.zeros((height,width))
                for row in range(0,height):
                    for column in range(0,width):
                        image[row][column]=fullFile[j][position+10+row*width+column];
                position +=sampleSize;
#               print(i)
#               print('character',character[i])
                im = iF.arrayToImage(image,height,width)
                #print(im)
                imResize=iF.resizeImage(im,info.maxWidth,info.maxHeight)
                #print(imResize)
                images[k] = iF.PIL2array(imResize);
                #print(images[k],k)
                k+=1
        return [characters,images,info.maxHeight,info.maxWidth]


    def infoGNT(path,name):
        #set path and open file
        os.chdir(path)
        with open(name, 'rb') as f:
            fullFile = f.readlines()[0];
        f.close();
        numSamples = 0;
        totalSize = 0;
        maxWidth=0;
        maxHeight=0;
        position = 0;
        while position < len(fullFile):
            sampleSize = fileFunc.byteToInt(fullFile[position:position+4]);
            maxWidth = max(fileFunc.byteToInt(fullFile[position+6:position+8]),maxWidth)
            maxHeight = max(fileFunc.byteToInt(fullFile[position+8:position+10]),maxHeight)
            numSamples+=1;
            position += sampleSize
            totalSize +=sampleSize;
        infoStruct = namedtuple("myStruct","numSamples maxHeight, maxWidth, totalSize")
        info = infoStruct(numSamples,maxHeight,maxWidth,totalSize)
        print (info)
        return info
    
    #find max width, max height and number of samples from a byte array holding gnt data
    def infoGNT2(array,totalFiles):
        #array = array[0] #must set as this;
        totalSize = 0;
        maxWidth=0;
        maxHeight=0;
        numSamples=np.zeros(totalFiles)
        for i in range (0,totalFiles):
            position = 0;
            while position < len(array[i]):
                sampleSize = fileFunc.byteToInt(array[i][position:position+4]);
                maxWidth = max(fileFunc.byteToInt(array[i][position+6:position+8]),maxWidth)
                maxHeight = max(fileFunc.byteToInt(array[i][position+8:position+10]),maxHeight)
                numSamples[i]+=1;
                position += sampleSize
                totalSize +=sampleSize;
            numSamples[i] =int(numSamples[i]-1);
        infoStruct = namedtuple("myStruct","numSamples maxHeight, maxWidth, totalSize")
        info = infoStruct(numSamples,maxHeight,maxWidth,totalSize)
        print (info)
        return info
    #function to read several gnt files into an array in byte form    
    def iterateOverFiles(path):
        #path is the folder containing subfolders containing all .gnt files
        totalFiles = 0
        source = 'C:/Users/Sebastian/Desktop/MLChinese/CASIA/HWDtest2' #left as example
        source = path
        for subdir, dirs, filenames in os.walk(source):
            totalFiles += len(filenames)
        print(totalFiles)
        
        fullFile = [None]*totalFiles
        for subdir, dirs, filenames in os.walk(source):
            for file in filenames:
                fullpath = os.path.join(subdir, file)
                with open(fullpath, 'rb') as openFile:
                    fullFile[filenames.index(file)] = openFile.readlines()[0]
                    openFile.close()
        return fullFile,totalFiles