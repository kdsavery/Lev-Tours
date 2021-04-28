# Version 1.2.2
# Imports
import logger as log
import math
import time
import random
import rssi
import statistics as stat
import subprocess
import sys
from threading import Thread
import turtle


#Constants
NETWORKS_NOT_DETECTED = 999
WORST_SIGNAL = -100
BEST_SIGNAL = 0
DEFAULT_SCAN_AMOUNT = 25
SCAN_LIMIT = 5


#Globals
interface = 'wlp2s0' # System dependent
rssi_scanner = rssi.RSSI_Scan(interface)
#ssids = ['NAU']
ssids = []

# Used within the GUI to display how many scans remain during setup
scansCompleted = 0

# Used to keep scanning wifi and estimating position
keep_scanning = False

def getScansCompleted():
    return scansCompleted

def setScansCompleted(num):
    global scansCompleted
    scansCompleted = 0

def getScanAmount():
    return DEFAULT_SCAN_AMOUNT

def start_scanning(nodes_to_scan):
    global keep_scanning
    keep_scanning = True
    RecurringScans(nodes_to_scan).start()

def stop_scanning():
    global keep_scanning
    keep_scanning = False


#Function Definitions
def adjustRange(sample):
    minSig = int(sample["minSig"])
    maxSig = int(sample["maxSig"])
    avgSig = float(sample["avgSig"])
    rangeInc = math.floor(((1 - avgSig/(WORST_SIGNAL*-1))*10))
    return [minSig-rangeInc, maxSig+rangeInc]

'''
Original Design November 2020
'''
def compareLocation(current, stored, location_names):
    for testPointInd in range(0, len(stored)):
        rating = 0.0
        penalties = math.floor(len(current)*0.1)
        for sample in current:
            currAddr = sample["mac"]
            AP_cnt = len(current)
            max_score = 100/AP_cnt #Sets max rating for location to be 100
            for storedSample in stored[testPointInd]:
                if currAddr == storedSample["mac"]:
                    currSignal = sample["signal"]*-1
                    minSig = int(storedSample["minSig"])
                    maxSig = int(storedSample["maxSig"])
                    adjusted = adjustRange(storedSample)
                    minDiff = minSig - adjusted[0]
                    maxDiff = adjusted[1] - maxSig
                    avgSig = float(storedSample['avgSig'])
                    avgQual = float(storedSample['qualAvg'])
                    minDist = avgSig - minSig
                    maxDist = maxSig - avgSig
                    if(minDist == 0.0):
                        minDist = 1
                    if(maxDist == 0.0):
                        maxDist = 1
                    #Sample signal is a match for stored data
                    if currSignal >= minSig and currSignal <= maxSig:
                        if currSignal < avgSig:
                            score = 1 - (avgSig - currSignal) / minDist
                            if(minDiff != 0):
                                score *= minDiff
                        else:
                            score = 1 - (currSignal - avgSig) / maxDist
                            if(maxDiff != 0):
                                score *= maxDiff
                        rating += (score*max_score)
                    #Sample signal is not a match for stored data
                    else:
                        if(currSignal < minSig):
                            penalty_amt = 0
                            temp = (minSig - currSignal) / minDist
                        else:
                            temp = (currSignal - maxSig) / maxDist
                        if(rating-temp >= 0.0):
                            if(penalties <= 0):
                                rating -= (temp*max_score)
                            else:
                                penalties = penalties - 1
                    break
        try:
            if(rating > maxRating):
                maxRating = rating
                maxLocation = location_names[testPointInd]

        except UnboundLocalError:
            maxRating = rating
            maxLocation = location_names[testPointInd]

    return maxLocation

def get_closest(ratings):
    if(ratings == []):
        return None
    max_rating = ratings[0][1]
    max_location = ratings[0][0]
    for index in range(1, len(ratings)):
        rating = ratings[index]
        if(rating[1] > max_rating):
            max_rating = rating[1]
            max_location = rating[0]
    return max_location

def gen_ranged(samples):
    newRangeData = []
    usedAddresses = []
    index = 0
    for sample in samples:
        currAddr = sample["mac"]
        if(currAddr in usedAddresses):
            continue
        usedAddresses.append(currAddr)
        signals = [sample["signal"]*-1]
        qualities = [int((sample["quality"].split("/"))[0])]
        for nextSample in samples[index+1:]:
            if(nextSample["mac"] == currAddr):
                signals.append(nextSample["signal"]*-1)
                qualities.append(int((sample["quality"].split("/"))[0]))
        signals = slim(signals)
        qualities = slim(qualities)
        minSignal = min(signals)
        maxSignal = max(signals)
        minQuality = min(qualities)
        maxQuality = max(qualities)
        signalAvg = round(sum(signals)/len(signals),2)
        qualityAvg = round(sum(qualities)/len(qualities),2)
        newRangeData.append({"mac":currAddr,
                     "avgSig":signalAvg,
                     "minSig":minSignal,
                     "maxSig":maxSignal,
                     "qualAvg":qualityAvg,
                     "minQual":minQuality,
                     "maxQual":maxQuality})

    return newRangeData

def gen_region_data(scan_amt):
    global scansCompleted
    allData = []
    for cnt in range(0, scan_amt):
        scans = network_pull()
        scansCompleted += 1
        for scan in scans:
            allData.append(scan)

    return allData

def median(values):
    medIndex = medianIndex(values)
    if(len(values) % 2 == 1):
        return values[medIndex]
    else:
        if(len(values) <= 2):
            return sum(values)/len(values)
        return (values[medIndex] + values[medIndex - 1])/2


def medianIndex(values):
    return int(math.floor(len(values)/2))

def network_pull():
        timeout_start = time.perf_counter()
        try:
            currentCapture = rssi_scanner.getAPinfo(networks=ssids, sudo=True)
            while(currentCapture == False or len(currentCapture) == 0):
                if(time.perf_counter() - timeout_start > 20.0):
                    return NETWORKS_NOT_DETECTED
                currentCapture = rssi_scanner.getAPinfo(networks=ssids, sudo=True)
        except:
            log.logging.error(" An error occured while trying to scan, scanning has been aborted")
            return []
        return currentCapture

def setup_scans():
    return gen_ranged(gen_region_data(DEFAULT_SCAN_AMOUNT))

def slim(values):
    newValues = values
    if(len(values) > 2):
        values.sort()
        avg = sum(values)/len(values)
        Q2_index = medianIndex(values)
        Q1 = median(values[:Q2_index])
        Q3 = median(values[Q2_index+1:])
        IQR = Q3-Q1
        lowerBound = Q1 - 1.5*IQR
        upperBound = Q3 + 1.5*IQR
        newValues = []
        for index in range(0, len(values)):
            if((values[index] <= upperBound) and (values[index] >= lowerBound)):
                newValues.append(values[index])
    return newValues

class RecurringScans(Thread):
    def __init__(self, scan_nodes):
        Thread.__init__(self)
        self.scan_nodes = scan_nodes
        self.all_data = []
        self.names = []
        for node in scan_nodes:
            if(not node.wifi_data == []):
                self.all_data.append(node.wifi_data)
                self.names.append(node.name)

    def run(self):
        global keep_scanning
        log.logging.info("Beginning Wi-Fi scans during building traversal")
        err_cnt = 0
        while(keep_scanning):
            current_scan = network_pull()
            if(not current_scan == []):
                try:
                    estimation = compareLocation(current_scan, self.all_data, self.names)
                    log.logging.info("POSITION ESTIMATE: " + estimation)
                except UnboundLocalError:
                    continue
                err_cnt = 0
                
            else:
                err_cnt += 1

            if(err_cnt == SCAN_LIMIT):
                log.logging.error(str(SCAN_LIMIT) + " Consecutive errors occured while attemping to scan Wi-FI, scanning stopped")
                keep_scanning = False
