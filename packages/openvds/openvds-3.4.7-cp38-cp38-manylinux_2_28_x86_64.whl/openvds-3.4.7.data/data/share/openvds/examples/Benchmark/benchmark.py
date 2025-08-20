###############################################################################
# <copyright>
# Copyright (c) 2023 Bluware Inc. All rights reserved.
#
# All rights are reserved. Reproduction or transmission in whole or in part,
# in any form or by any means, electronic, mechanical or otherwise,
# is prohibited without the prior written permission of the copyright owner.
# </copyright>
###############################################################################

import openvds
import sys

import numpy as np
import math
import os
import csv
import socket

import argparse
import re

from timeit import default_timer as timer
from IPython.display import clear_output

class Configuration:
    uri: str
    connection: str
    hostname: str
    api: str
    apiVersion: str
    testTypes: []
    testCompressionLevels: []
    testRepeat: int


def connectVDSVolume(configuration, level):
    vdsVolume = None
    if level == 0:
        vdsVolume = openvds.open(configuration.uri, configuration.connection)
    else:
        vdsVolume = openvds.openWithAdaptiveCompressionRatio(configuration.uri, configuration.connection, level)

    return vdsVolume

def updateProgress(startTime, dataLoaded, progress):
    endTime = timer()

    # Update progress only every 10th of a second
    global prevUpdateTime
    try:
        if (progress < 1.0) and (endTime - prevUpdateTime) < 0.1:
            return
    except:
        pass
    prevUpdateTime = endTime

    MBLoaded = dataLoaded / (1024 * 1024) #4 for size of float
    timeUsed = endTime - startTime

def runRandomAccessSpeedTest(configuration, vdsVolume, repeat, level, testType):
    queueMax = 8
    randomQueries = 100

    accessor = configuration.getVolumeDataAccess(vdsVolume)
    layout = configuration.getVolumeDataLayout(vdsVolume)

    requestSizeDim0 = min(400, int(layout.getDimensionNumSamples(0) * 0.2))
    requestSizeDim1 = min(500, int(layout.getDimensionNumSamples(1) * 0.3))
    requestSizeDim2 = min(600, int(layout.getDimensionNumSamples(2) * 0.4))

    resultArrays = [np.empty(shape=(requestSizeDim2, requestSizeDim1, requestSizeDim0), dtype=np.float32) for _ in range(queueMax)]

    requests = [None] * queueMax

    inQueue = 0
    iNext = 0

    dataLoaded = 0

    np.random.seed(42)

    startTime = timer()

    for randomQuery in range(randomQueries):

        qmin = [ np.random.randint(0,layout.getDimensionNumSamples(0)-requestSizeDim0)
                , np.random.randint(0,layout.getDimensionNumSamples(1)-requestSizeDim1)
                , np.random.randint(0,layout.getDimensionNumSamples(2)-requestSizeDim2) ]

        qmax = [qmin[0] + requestSizeDim0
                ,qmin[1] + requestSizeDim1
                ,qmin[2] + requestSizeDim2]

        requests[iNext % queueMax] = configuration.requestVolumeSubset(accessor, qmin, qmax, layout.getChannelFormat(0), resultArrays[iNext % queueMax])

        iNext+=1
        inQueue+=1

        if inQueue == queueMax:
            requests[iNext % queueMax].waitForCompletion()
            dataLoaded += requests[iNext % queueMax].data.size * 4
            inQueue-=1
            updateProgress(startTime, dataLoaded, (randomQuery - inQueue)  / (randomQueries - 1))


    while inQueue > 0:
        iNext-=1
        requests[iNext % queueMax].waitForCompletion()
        dataLoaded += requests[iNext % queueMax].data.size * 4
        inQueue-=1
        updateProgress(startTime, dataLoaded, (randomQuery - inQueue)  / (randomQueries - 1))


    endTime = timer()

    MBLoaded = dataLoaded / (1024 * 1024)
    timeUsed = endTime - startTime

    cvs_results = printResults(configuration, testType, repeat, level, MBLoaded, timeUsed)

    del resultArrays

    return cvs_results

def runSpeedTest(configuration, vdsVolume, repeat, level, testType):
    accessor = configuration.getVolumeDataAccess(vdsVolume)
    layout = configuration.getVolumeDataLayout(vdsVolume)
    dim2Size = min(layout.getDimensionNumSamples(0), 100)

    resultBuffer = np.empty(shape=(dim2Size, layout.getDimensionNumSamples(1), layout.getDimensionNumSamples(2)), dtype=np.float32)

    startTime = timer()

    qmin = [0,0,0]
    qmax = [layout.getDimensionNumSamples(0), layout.getDimensionNumSamples(1), dim2Size]
    request = configuration.requestVolumeSubset(accessor, qmin, qmax, layout.getChannelFormat(0))

    request.waitForCompletion()

    endTime = timer()
    dataLoaded = request.data.size * 4 # floating point

    MBLoaded = dataLoaded / (1024 * 1024)
    timeUsed = endTime - startTime

    return printResults(configuration, testType, repeat, level, MBLoaded, timeUsed)

def printResults(configuration, testType, repeat, level, MBLoaded, timeUsed):
    clear_output(wait=True)
    print ("{:^18}{:^17}{:^14}{:^14}{:^14}{:^14}{:^14.3f}{:^14.3f}{:^14.3f}{:^14.3f}".format(configuration.hostname, testType, configuration.api, configuration.apiVersion, repeat, level, MBLoaded, timeUsed, MBLoaded/timeUsed, (MBLoaded * 8) / (timeUsed * 1024)))
    return [configuration.hostname, testType, configuration.api, configuration.apiVersion, repeat, level, MBLoaded, timeUsed, MBLoaded/timeUsed, (MBLoaded * 8) / (timeUsed * 1024)]

def runTests(cnfiguration):
    cvs_results = [];
    for testType in configuration.testTypes:

        for level in configuration.testCompressionLevels:
            repeat = 0

            while (repeat < configuration.testRepeat):
                repeat+=1

                vdsVolume = connectVDSVolume(configuration, level)


                if testType == 'RandomRequets':
                    cvs_results.append(runRandomAccessSpeedTest(configuration, vdsVolume, repeat, level, testType))
                elif testType == 'OneLargeRequest':
                    cvs_results.append(runSpeedTest(configuration, vdsVolume, repeat, level, testType))
                else:
                    print('oh oh! Invalid testType')

                del vdsVolume
    return cvs_results

def openvdsRequestVolumeSubset(accessManager, qmin, qmax, format, data_out = None):
    return accessManager.requestVolumeSubset(data_out=data_out, min=qmin, max=qmax, format=format)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Benchmark VDS apis on cloud platform.')
    parser.add_argument('--uri', help='uri for where to read the data from', required=True)
    parser.add_argument('--connection', help='connection string for parameters to the uri', default="")
    args = parser.parse_args()

    configuration = Configuration()
    configuration.uri = args.uri
    configuration.connection = args.connection
    configuration.hostname = socket.gethostname()

    configuration.api = openvds.getOpenVDSName()
    configuration.apiVersion = openvds.getOpenVDSVersion()
    configuration.getVolumeDataAccess = openvds.VolumeDataAccessManager
    configuration.getVolumeDataLayout = openvds.getLayout
    configuration.requestVolumeSubset = openvdsRequestVolumeSubset

    configuration.testTypes = ['OneLargeRequest', 'RandomRequets']

    configuration.testCompressionLevels = [0, 1, 10, 40, 100]

    configuration.testRepeat = 1

    fileName = "results-{}-{}.csv".format(configuration.hostname, configuration.api)

    print ("{:^18}{:^17}{:^14}{:^14}{:^14}{:^14}{:^14}{:^14}{:^14}{:^14}".format('Instance','Test type','API','Version', 'Run#', 'Compression', 'MB', 'Time', 'MB/s', 'GBit/s'))
    csvList = []

    csvList.append(['Instance','Test type','API','Version', 'Run#','Compression','MB','Time','MB/s','GBit/s','Host'])

    csvList = csvList + runTests(configuration)

    with open(fileName, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(csvList)
