import math
import os
import numpy as np
import datetime
import csv
from Read_images import *
from scipy.ndimage import imread

# Turn off warnings
import warnings
warnings.filterwarnings(action='ignore')

# global module variables

logDir = ''
logFile = ''
lastLogTime = ''
cloudBucket = ''
localPrefix = ''

def initRootFolders(bucketName='', localIOPath=''):

    global cloudBucket
    global localPrefix

    if bucketName != '':
        import google.datalab.storage as storage
        cloudBucket = storage.Bucket(bucketName)
    
    localPrefix = localIOPath

def initLog(logDirIn, suffix=''):
    
    global logDir
    global logFile
    global lastLogTime
    
    logDir = logDirIn
    logFile = logDir + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + suffix + '.log'
    lastLogTime = datetime.datetime.now()
    log('Log file initialized')
    
def log(message):

    global lastLogTime
    global logFile
    
    now = datetime.datetime.now()
    line =  '    ' + str(now - lastLogTime) + '\n' + str(now) + '    ' + message + '\n'

    with open(filePath(logFile), 'a') as f:
        f.write(line)

    lastLogTime = now

def filenames(folder):

    global cloudBucket
    global localPrefix

    if folder[:6] == 'cloud/':

        filenames = cloudBucket.objects(prefix = folder[6:], delimiter = '/')
        filenames = ['cloud/' + x.key for x in filenames if x.key[-1] != '/']

    else:

        # It's an ordinary folder
        filenames = os.listdir(localPrefix + folder[6:])
        filenames = [folder + x for x in filenames]

    return filenames

def filePath(fileIn):
    """Download from bucket, or fill in local path prefix"""
    
    global cloudBucket
    global localPrefix

    # Get the file extenion
    dmy, extension = os.path.splitext(fileIn)

    if fileIn[:6] == 'cloud/':

        # It's a file in a cloud bucket.  Transfer to local temporary file.

        # Get bucket path to file
        bucketFile = fileIn[6:]

        # Make a name for the temporary file
        file = 'tmp' + extension

        # Transfer to temporary file
        x = cloudBucket.object(bucketFile).read_stream()
        with open(file, 'wb') as f: f.write(x)

    else:

        # It's an ordinary local file
        file = localPrefix + fileIn[6:]
    
    return file

def loadFile(fileIn):

    global cloudBucket
    global localPrefix

    # Get the file extenion
    dmy, extension = os.path.splitext(fileIn)


    # Download from cloud, or fill in local path prefix
    file = filePath(fileIn)
    
    # Read file
    data = 0
    if extension == '.png':
        data = np.array(imread(file), dtype=np.float32)/255.
    elif extension == '.a3d':
        data = read_data(file)

    return data