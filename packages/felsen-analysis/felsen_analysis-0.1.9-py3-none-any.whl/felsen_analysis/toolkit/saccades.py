import numpy as np
from felsen_analysis.toolkit.process import AnalysisObject
import math
from scipy import stats


def parseSaccadeType(h5file, start=None, stop=None, saccades=None):
    """
    This function determines which saccades are spontaneous and which are driven
    and returns both arrays
    """
    session = AnalysisObject(h5file)
    if start is None:
        start = session.load('stimuli/dg/grating/timestamps')
    if stop is None:
        stop = session.load('stimuli/dg/iti/timestamps')
    if saccades is None:
        saccades = session.load('saccades/predicted/left/timestamps')[:, 0]
    spontaneous = list()
    driven = list()
    for i, stopTime in enumerate(stop):
        try:
            startTime = start[i + 1]
        except:
            continue
        mask = np.logical_and(saccades > stopTime, saccades < startTime)
        masked = saccades[mask]
        if masked.any():
            masked = list(masked)
            for element in masked:
                spontaneous.append(element)

    spontaneous = np.array(spontaneous)
    driven = list()
    for sac in saccades:
        if sac not in spontaneous:
            driven.append(sac)
    driven = np.array(driven)
    return driven, spontaneous

def calculateSaccadeAmplitudes(h5file, saccades, pose=None, frameTimes=None, totalSaccadeTimes=None, saccadeIndices=None, endTimes=None):
    """
    Input either driven or spontaneous saccades and calculate their amplitudes
    """
    session = AnalysisObject(h5file)
    if pose is None:
        pose = session.load('pose/filtered')
    if frameTimes is None:
        frameTimes = session.load('frames/left/timestamps')
    if totalSaccadeTimes is None:
        totalSaccadeTimes = session.load('saccades/predicted/left/timestamps')[:, 0]
    subsetIndices = list()
    for time in saccades:
        sub = np.where(totalSaccadeTimes == time)[0]
        if sub.size == 1:
            subsetIndices.append(int(sub))
    if saccadeIndices is None:
        saccadeIndices = session.load('saccades/predicted/left/indices')
    amplitudes = list()
    for sac in subsetIndices:
        startIndex = saccadeIndices[sac]
        if endTimes is None:
            endTimes = session.load('saccades/predicted/left/timestamps')[:, 1]
        endTime = endTimes[sac]
        if endTime.size != 1:
            amplitudes.append(0)
            continue
        relativeEnd = abs(frameTimes - endTime)
        endShape = np.where(relativeEnd == np.min(relativeEnd))[0].shape[0]
        if endShape == 2:
            endIndex = np.where(relativeEnd == np.min(relativeEnd))[0][0]
        else:
            endIndex = int(np.where(relativeEnd == np.min(relativeEnd))[0])
        startPoint = pose[startIndex, 0]
        endPoint = pose[endIndex, 0]
        amplitude = endPoint - startPoint
        amplitudes.append(float(amplitude))
    return amplitudes

def calculateSaccadeStartPoint(h5file, saccades, pose=None, totalSaccadeTimes=None, saccadeIndices=None):
    """
    Input either driven or spontaneous saccades and calculate their start point
    """
    session = AnalysisObject(h5file)
    if pose is None:
        pose = session.load('pose/filtered')
    if totalSaccadeTimes is None:
        totalSaccadeTimes = session.load('saccades/predicted/left/timestamps')[:, 0]
    subsetIndices = list()
    for time in saccades:
        sub = np.where(totalSaccadeTimes == time)[0]
        if sub.size == 1:
            subsetIndices.append(int(sub))
    if saccadeIndices is None:
        saccadeIndices = session.load('saccades/predicted/left/indices')
    indicesToUse = saccadeIndices[subsetIndices]
    startPoints = list()
    for sac in indicesToUse:
        startIndex = sac
        startPoint = pose[startIndex, 0]
        if startPoint.size != 1:
            startPoints.append(0)
        else:
            startPoints.append(float(startPoint))
    return startPoints

def calculateSaccadeEndPoint(h5file, saccades, pose=None, frameTimes=None, totalSaccadeTimes=None, endTimes=None):
    """
    Input either driven or spontaneous saccades and calculate their end point
    """
    session = AnalysisObject(h5file)
    if pose is None:
        pose = session.load('pose/filtered')
    if frameTimes is None:
        frameTimes = session.load('frames/left/timestamps')
    if totalSaccadeTimes is None:
        totalSaccadeTimes = session.load('saccades/predicted/left/timestamps')[:, 0]
    subsetIndices = list()
    for time in saccades:
        sub = np.where(totalSaccadeTimes == time)[0]
        if sub.size == 1:
            subsetIndices.append(int(sub))
    endPoints = list()
    for sac in subsetIndices:
        if endTimes is None:
            endTimes = session.load('saccades/predicted/left/timestamps')[:, 1]
        endTime = endTimes[sac]
        if endTime.size != 1:
            endPoints.append(0)
            continue
        relativeEnd = abs(frameTimes - endTime)
        endShape = np.where(relativeEnd == np.min(relativeEnd))[0].shape[0]
        if endShape == 2:
            endIndex = np.where(relativeEnd == np.min(relativeEnd))[0][0]
        else:
            endIndex = int(np.where(relativeEnd == np.min(relativeEnd))[0])
        endPoint = pose[endIndex, 0]
        endPoints.append(float(endPoint))
    return endPoints

def computeNormalizedFiringRate(h5file, unitsToAnalyze, events, window):
    """
    Compute & Z-score the firing rate of all neurons for all saccades
    """
    session = AnalysisObject(h5file)
    population = session._population()
    nanCount = np.sum(np.isnan(events))
    FRlist = np.zeros((len(unitsToAnalyze), len(events) - nanCount))
    k = 0
    for i, event in enumerate(events):
        if np.isnan(event):
            print(f'Event {i} is NaN')
            continue
        j = 0
        for unit in population:
            if unit.cluster not in unitsToAnalyze:
                continue
            spikeTimes = unit.timestamps
            start = events[i] + window[0]
            end = events[i] + window[1]
            mask = np.logical_and(spikeTimes > start, spikeTimes < end)
            activity = len(spikeTimes[mask])/0.3
            FRlist[j, k] = activity
            j = j+1
        k = k + 1
    z = stats.zscore(FRlist, axis=1, nan_policy='omit')
    return z

def binFiringRatesbyMetric(z, ampList, startList, endList, unit, binsize):
    """
    Puts firing rates for all saccades for a given unit into bins, split up by metrics
    Preps data to plot a single unit example of firing rate by saccade metric
    But we bin it so we can actually see stuff or else it looks gross and incomprehensible
    Yes I know returning 6 things is a crime
    """
    ampAvg = list()
    startAvg = list()
    endAvg = list()
    a = sorted(ampList)
    s = sorted(startList)
    e = sorted(endList)
    lists = [np.array(ampList), np.array(startList), np.array(endList)]
    binStartA = list()
    binStartS = list()
    binStartE = list()

    for i, feature in enumerate([a, s, e]):
        bins = np.arange(0, len(feature), len(feature)/binsize)
        for k in bins:
            j = int(k)
            values = feature[j:int(j+len(feature)/binsize)]
            inds = list()
            for value in values:
                ind = np.where(lists[i] == value)[0]
                if ind.shape == (1,):
                    inds.append(int(ind))
                elif ind.shape == (0,):
                    continue
                else:
                    for n in ind:
                        inds.append(int(n))         
            data = z[unit, inds]
            avg = np.nanmean(data)
            if i == 0:
                ampAvg.append(avg)
                if len(values) == 0:
                    binStartA.append(len(feature))
                else:
                    binStartA.append(np.nanmin(values))
            elif i == 1:
                startAvg.append(avg)
                if len(values) == 0:
                    binStartS.append(len(feature))
                else:
                    binStartS.append(np.nanmin(values))
            elif i == 2:
                endAvg.append(avg)
                if len(values) == 0:
                    binStartE.append(len(feature))
                else:
                    binStartE.append(np.nanmin(values))
    return ampAvg, startAvg, endAvg, binStartA, binStartS, binStartE

def computeBinMiddles(binStartA, binStartS, binStartE):
    """
    Takes bin starts and computes the middle of each bin for plotting
    """
    binMidA = list()
    relListA = list()
    for i, binA in enumerate(binStartA):
        try:
            relative = (binStartA[i + 1] - binA)/2
            relListA.append(relative)
            binMidA.append(binA + relative)
        except:
            binMidA.append(binA + np.mean(relListA))
    binMidS = list()
    relListS = list()
    for i, binS in enumerate(binStartS):
        try:
            relative = (binStartS[i + 1] - binS)/2
            relListS.append(relative)
            binMidS.append(binS + relative)
        except:
            binMidS.append(binS + np.mean(relListS))
    binMidE = list()
    relListE = list()
    for i, binE in enumerate(binStartE):
        try:
            relative = (binStartE[i + 1] - binE)/2
            relListE.append(relative)
            binMidE.append(binE + relative)
        except:
            binMidE.append(binE + np.mean(relListE))
    return binMidA, binMidS, binMidE


def generateSaccadeMetricArray(h5file, ampList, startList, endList):
    """
    Assemble all saccade metrics into 1 array for ease of use
    Required for using the prediction module
    """
    session = AnalysisObject(h5file)
    sacMetrics = np.zeros((len(ampList), 3))
    sacMetrics[:, 0] = ampList
    sacMetrics[:, 1] = startList
    sacMetrics[:, 2] = endList
    return sacMetrics

def binFiringRatesTrialByTrial(z, ampList, startList, endList, unit, binsize):
    """
    Puts firing rates for all saccades for a given unit into bins, split up by metrics
    Preps data to plot a single unit example of firing rate by saccade metric
    Same as other binning firing rates function returns all firing rates for all trials, not an average
    Also doesn't return bin starts bc idc
    """
    a = sorted(ampList)
    s = sorted(startList)
    e = sorted(endList)
    ampFR = list()
    startFR = list()
    endFR = list()
    lists = [np.array(ampList), np.array(startList), np.array(endList)]
    for i, feature in enumerate([a, s, e]):
        bins = np.arange(0, len(feature), len(feature)/binsize)
        for k in bins:
            j = int(k)
            values = feature[j:int(j+len(feature)/binsize)]
            inds = list()
            for value in values:
                ind = np.where(lists[i] == value)[0]
                if ind.shape == (1,):
                    inds.append(int(ind))
                elif ind.shape == (0,):
                    continue
                else:
                    for n in ind:
                        inds.append(int(n))         
            data = z[unit, inds]
            if i == 0:
                ampFR.append(data)
            elif i == 1:
                startFR.append(data)
            elif i == 2:
                endFR.append(data)
    return ampFR, startFR, endFR
