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
    def whichUser(user):
        trainDataPathElliot = 'C:/Users/ellio/Documents/training data/'
        trainDataPathSeb = 'C:\\Users\\Sebastian\\Desktop\\MLChinese\\CASIA\\1.0'
        rawDataPathSeb = 'C:\\Users\\Sebastian\\Desktop\\MLChinese\\CASIA\\1.0'
        rawDataPathElliot = 'C:\\Users\\ellio\\Documents\\training data\\'
        SebLOGDIR = r'C:/Users/Sebastian/Desktop/MLChinese/Saved_runs'
        elliotLOGDIR = r'C:/Users/ellio/Anaconda3/Lib/site-packages/tensorflow/tmp/'
        if user == "Elliot":
            return trainDataPathElliot, elliotLOGDIR, rawDataPathElliot
        else:
            return trainDataPathSeb, SebLOGDIR, rawDataPathSeb
    
    def byteToInt(byte,byteOrder='little'):
        return int.from_bytes(byte, byteorder=byteOrder)

    def readByte(name):
        allBytes = []
        with open(name, "rb") as f:
            byte = f.read(1) #read in byte (then move on)
            allBytes.append(byte) #if we don't include this line, we miss the first byte
            while byte != b"":
                # Do stuff with byte.
                byte = f.read(1)
                allBytes.append(byte) #creates list of all bytes, each byte has a separate index
        f.close()
        allByte = b''.join(map(bytes,allBytes)) #concatenates list of bytes
        return allByte
    
    #Function that reads the NPZ file 'name' at 'path' and returns the file object
    def readNPZ(path,name,labelName,imageName):
        fullPath = os.path.join(path, name)
        with open(fullPath, 'rb') as ifs:
            fileNPZ = np.load(ifs)
            return fileNPZ[labelName],fileNPZ[imageName]
        
    #function that saves a list of arrays 'namedArrays' to the file 'name' at
    #location 'path' with the option of compression 'compressed'      
    def saveNPZ(path,name,compressed=False,**namedArrays):
        print("save")
        fullPath = os.path.join(path, name)
        with open(fullPath, 'wb') as ofs:
            if compressed:
                np.savez_compressed(ofs,**namedArrays)
            else:
                np.savez(ofs,**namedArrays)
        ofs.close();

    def arraysFromGNT(fullFile,info,imageSize):
        print("arraysFromGNT")
        #create arrays to store data read in
        totalSamples = int(np.sum(info.numSamples));
        characters = np.zeros(totalSamples,np.unicode);
        #images = np.zeros((totalSamples,info.maxWidth*info.maxHeight))
        reducedSize = imageSize
        images = np.zeros((totalSamples,reducedSize*reducedSize)) #images saved as reduced versions
        #place data into arrays
        k=0
        position = 0;
        for i in range(int(info.numSamples)):
            sampleSize = fileFunc.byteToInt(fullFile[position:position+4]);
            characters[k] = fullFile[position+4:position+6].decode('gbk');
            width = fileFunc.byteToInt(fullFile[position+6:position+8]);
            height = fileFunc.byteToInt(fullFile[position+8:position+10]);
            image = np.zeros((height,width))
            for row in range(0,height):
                for column in range(0,width):
                    image[row][column]=fullFile[position+10+row*width+column];
            position +=sampleSize;
            #make all images the same size and reshape them into a 1D vector
            imageReduced = iF.scaleImage(image,reducedSize)
            images[k] = np.reshape(imageReduced,reducedSize*reducedSize)
            #images[k] = iF.binarizeArray(images[k],255)
            #im = iF.arrayToImage(image,height,width)
            #imResize=iF.resizeImage(im,info.maxWidth,info.maxHeight)
            #images[k] = iF.PIL2array(imResize);
            #print(images[k],k)
            k+=1
            """Only image.astype(np.uint8) can be outputted as an image"""
        return [characters, images.astype(np.uint8), info.maxHeight,info.maxWidth]

    def infoGNT(array):
        """find max width, max height and number of samples from a byte array holding gnt data"""
        #array = array[0] #must set as this;
        print("infoGNT")
        totalSize = 0;
        maxWidth=0;
        maxHeight=0;
        minWidth = 400; #arbitrarily large number
        minHeight = 400;
        position = 0;
        numSamples=0
        while position < len(array):
            sampleSize = fileFunc.byteToInt(array[position:position+4]);
            maxWidth = max(fileFunc.byteToInt(array[position+6:position+8]),maxWidth)
            maxHeight = max(fileFunc.byteToInt(array[position+8:position+10]),maxHeight)
            minWidth = min(fileFunc.byteToInt(array[position+6:position+8]),minWidth)
            minHeight = min(fileFunc.byteToInt(array[position+8:position+10]),minHeight)
            numSamples += 1;
            position += sampleSize
            totalSize += sampleSize;
        numSamples = int(numSamples-1);#remove excess bytes
        infoStruct = namedtuple("myStruct","numSamples maxHeight, maxWidth, minHeight, minWidth, totalSize")
        info = infoStruct(numSamples,maxHeight,maxWidth,minHeight,minWidth,totalSize)
        print (info)
        return info
    
    def arraysFromDGR(array,numFiles):
        position=0
        while position <len(array):
            headerSize=fileFunc.byteToInt(array[position:position+4])
            formatCode=array[position+4:position+12]
            illustration=234
            
            
            
        
        
    def iterateOverFiles(path):
        """function to read several gnt files into an array in byte form"""
        #path is the folder containing subfolders containing all .gnt files
        totalFiles = 0
        for subdir, dirs, filenames in os.walk(path):
            totalFiles += len(filenames)
        print("total Files:",totalFiles)
        
        fullFile = [None]*totalFiles
        for subdir, dirs, filenames in os.walk(path):
            for file in filenames:
                fullpath = os.path.join(subdir, file)
                with open(fullpath, 'rb') as openFile:
                    fullFile[filenames.index(file)] = fileFunc.readByte(fullpath)
                    openFile.close()
        return fullFile,totalFiles

    