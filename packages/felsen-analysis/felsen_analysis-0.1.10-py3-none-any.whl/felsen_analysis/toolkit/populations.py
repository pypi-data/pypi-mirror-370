from felsen_analysis.toolkit.process import AnalysisObject
from felsen_analysis.backend.helper import randmat
import unit_localizer as ul
import numpy as np
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from scipy.ndimage.filters import gaussian_filter1d


def defineQualityUnits(h5file, clusterFile, ampCutoff=None, presenceRatio=None, firingRate=None, isiViol=None, qualityLabels=None):
    """
    This function filters all units by quality metrics and returns a list of unit cluster numbers assigned to good quality units
    Not necessary to use if using one of the definePopulation functions as it is built in to those functions (ie definePremotorPopulation)
    Helpful if you want to use all units in a recording, not just a predefined population, but want good quality units only
    """
    session = AnalysisObject(h5file)
    population = session._population()
    if ampCutoff is None:
        ampCutoff = session.load('metrics/ac')
        presenceRatio = session.load('metrics/pr')
        firingRate = session.load('metrics/fr')
        isiViol = session.load('metrics/rpvr')
        qualityLabels = session.load('metrics/ql')
    qualityUnits = list()
    for index, unit in enumerate(population):
        if qualityLabels is not None and qualityLabels[index] in (0, 1):
            continue
        if ampCutoff[index] <= 0.1:
            if presenceRatio[index] >= 0.9:
             if firingRate[index] >= 0.2:
                if isiViol[index] <= 0.5:
                    qualityUnits.append(unit.cluster)
    return qualityUnits

def definePremotorPopulation(h5file, clusterFile, allenFile=None, labels=None, zetaNasal=None, zetaTemporal=None, ampCutoff=None, presenceRatio=None, firingRate=None, isiViol=None, qualityLabels=None):
    """
    This function filters your population of neurons and pulls out premotor neurons based on ZETA test results
    """
    session = AnalysisObject(h5file)
    if labels is None:
        labels = session.load('nptracer/labels')
    if allenFile is None:
        brainAreas = ul.translateBrainAreaIdentities(labels) 
    else:
        brainAreas = ul.translateBrainAreaIdentities(labels, allenFile) 
    spikeClustersFile = clusterFile
    uniqueSpikeClusters = np.unique(np.load(spikeClustersFile))
    if zetaNasal is None:
        zetaNasal = session.load('zeta/saccade/nasal/p')
        zetaTemporal = session.load('zeta/saccade/temporal/p')
    if ampCutoff is None:
        ampCutoff = session.load('metrics/ac')
        presenceRatio = session.load('metrics/pr')
        firingRate = session.load('metrics/fr')
        isiViol = session.load('metrics/rpvr')
        qualityLabels = session.load('metrics/ql')
    premotorUnitsZeta = list()
    for index, pVal in enumerate(zetaNasal):
        if brainAreas[index] in ['SCsg','SCop', 'SCig', 'SCiw', 'SCdg']:
            pNasal = pVal
            pTemporal = zetaTemporal[index]
            if pNasal < pTemporal:
                p = pNasal
            elif pTemporal < pNasal:
                p = pTemporal
            if p < 0.05:
                if qualityLabels is not None and qualityLabels[index] in (0, 1):
                        continue
                if ampCutoff[index] <= 0.1:
                    if presenceRatio[index] >= 0.9:
                        if firingRate[index] >= 0.2:
                            if isiViol[index] <= 0.5:
                                unit = uniqueSpikeClusters[index]
                                premotorUnitsZeta.append(unit)

    return premotorUnitsZeta

def definePremotorPopulationExclusive(h5file, clusterFile):
    """
    This function defines the population of neurons that have only premotor and no visual activity
    """
    premotorUnitsExclusive = list()
    premotorUnitsAll = definePremotorPopulation(h5file, clusterFile)
    visualUnitsAll = defineVisualPopulation(h5file, clusterFile)
    visuomotorUnits = defineVisuomotorPopulation(premotorUnitsAll, visualUnitsAll)
    for unit in premotorUnitsAll:
        if unit not in visuomotorUnits:
            premotorUnitsExclusive.append(unit)
    return premotorUnitsExclusive

def defineVisualPopulationExclusive(h5file, clusterFile):
    """
    This function defines the population of neurons that have only premotor and no visual activity
    """
    visualUnitsExclusive = list()
    premotorUnitsAll = definePremotorPopulation(h5file, clusterFile)
    visualUnitsAll = defineVisualPopulation(h5file, clusterFile)
    visuomotorUnits = defineVisuomotorPopulation(premotorUnitsAll, visualUnitsAll)
    for unit in visualUnitsAll:
        if unit not in visuomotorUnits:
            visualUnitsExclusive.append(unit)
    return visualUnitsExclusive
    
def defineVisualPopulation(h5file, clusterFile, allenFile=None, labels=None, zetaLeft=None, zetaRight=None, ampCutoff=None, presenceRatio=None, firingRate=None, isiViol=None, qualityLabels=None):
    """
    This function filters your population of neurons and pulls out visual neurons based on ZETA test results
    """
    session = AnalysisObject(h5file)
    if labels is None:
        labels = session.load('nptracer/labels')
    #spikeClustersFile = session.home.joinpath('ephys/sorting/manual/spike_clusters.npy')
    spikeClustersFile = clusterFile
    uniqueSpikeClusters = np.unique(np.load(spikeClustersFile))
    if allenFile is None:
        brainAreas = ul.translateBrainAreaIdentities(labels) 
    else:
        brainAreas = ul.translateBrainAreaIdentities(labels, allenFile)
    if zetaLeft is None:
        zetaLeft = session.load('zeta/probe/left/p')
        zetaRight = session.load('zeta/probe/right/p')
    if ampCutoff is None:
        ampCutoff = session.load('metrics/ac')
        presenceRatio = session.load('metrics/pr')
        firingRate = session.load('metrics/fr')
        isiViol = session.load('metrics/rpvr')
        qualityLabels = session.load('metrics/ql')
    visualUnitsZeta = list()
    for index, pVal in enumerate(zetaLeft):
        if brainAreas[index] in ['SCsg','SCop', 'SCig', 'SCiw', 'SCdg']:
            pLeft = pVal
            pRight = zetaRight[index]
            if pLeft < pRight:
                p = pLeft
            elif pRight < pLeft:
                p = pRight
            if p < 0.05:
                if qualityLabels is not None and qualityLabels[index] in (0, 1):
                        continue
                if ampCutoff[index] <= 0.1:
                    if presenceRatio[index] >= 0.9:
                        if firingRate[index] >= 0.2:
                            if isiViol[index] <= 0.5:
                                unit = uniqueSpikeClusters[index]
                                visualUnitsZeta.append(unit)
    return visualUnitsZeta

def defineVisuomotorPopulation(premotorUnits, visualUnits):
    """
    This function finds which units are both visual and motor
    """
    visuomotorUnits = list()
    for unit in premotorUnits:
        if unit in visualUnits:
            visuomotorUnits.append(unit)
    return visuomotorUnits

def createTrialArray(h5file, timeBins, units, trials):
    """
    This function creates a list of len(trials) where each line is a units x 11 time bins array of spiking activity 
    This is the first step to running a PCA analysis that looks at population activity over time
    """
    trialList = list()
    session = AnalysisObject(h5file)
    #population = Population(session)
    population = session._population()
    for trial in trials:
        unitArray = np.zeros((len(units), 10))
        ind = 0
        for unit in population:
            if unit.cluster in units:
                spikeTimes = unit.timestamps
                t1 = trial + timeBins[0]
                t2 = trial + timeBins[1]
                t3 = trial + timeBins[2]
                t4 = trial + timeBins[3]
                t5 = trial + timeBins[4]
                t6 = trial + timeBins[5]
                t7 = trial + timeBins[6]
                t8 = trial + timeBins[7]
                t9 = trial + timeBins[8]
                t10 = trial + timeBins[9]
                t11 = trial + timeBins[10]
                mask1 = np.logical_and(spikeTimes >= t1, spikeTimes < t2)
                a = len(spikeTimes[mask1])/0.3
                mask2 = np.logical_and(spikeTimes >= t2, spikeTimes < t3)
                b = len(spikeTimes[mask2])/0.3
                mask3 = np.logical_and(spikeTimes >= t3, spikeTimes < t4)
                c = len(spikeTimes[mask3])/0.3
                mask4 = np.logical_and(spikeTimes >= t4, spikeTimes < t5)
                d = len(spikeTimes[mask4])/0.3
                mask5 = np.logical_and(spikeTimes >= t5, spikeTimes < t6)
                e = len(spikeTimes[mask5])/0.3
                mask6 = np.logical_and(spikeTimes >= t6, spikeTimes < t7)
                f = len(spikeTimes[mask6])/0.3
                mask7 = np.logical_and(spikeTimes >= t7, spikeTimes < t8)
                g = len(spikeTimes[mask7])/0.3
                mask8 = np.logical_and(spikeTimes >= t8, spikeTimes < t9)
                h = len(spikeTimes[mask8])/0.3
                mask9 = np.logical_and(spikeTimes >= t9, spikeTimes < t10)
                i = len(spikeTimes[mask9])/0.3
                mask10 = np.logical_and(spikeTimes >= t10, spikeTimes < t11)
                j = len(spikeTimes[mask10])/0.3
                fr = [a, b, c, d, e, f, g, h, i, j]
                unitArray[ind, :] = fr
                ind = ind + 1
        trialList.append(unitArray)
    return trialList

def specifyTrialTypes(h5file, saccade=True, sacLabels=None, tts=None): 
    """
    Lets you specify what different trial types you want to measure population responses to
    """
    session = AnalysisObject(h5file)
    if saccade==True:
        if sacLabels is None:
            sacLabels = session.load('saccades/predicted/left/labels') #contra = 1, ipsi = -1
        trial_type_tmp = sacLabels
    elif saccade==False:
        if tts is None:
            tts = session.load('stimuli/dg/probe/tts')
        typeCode = list() #perisaccadic = 0, extrasaccadic = 2
        for t in tts:
            if abs(t) < 0.1:
                typeCode.append(0)
            else:
                typeCode.append(2)
        trial_type_tmp = np.array(typeCode)
    trial_type = list()
    for element in trial_type_tmp:
        if element == -1:
            trial_type.append('Ipsi')
        elif element == 1:
            trial_type.append('Contra')
        elif element == 0:
            trial_type.append('Perisaccadic')
        elif element == 2:
            trial_type.append('Extrasaccadic')
    trial_types = np.unique(trial_type)
    t_type_ind = [np.argwhere(np.array(trial_type) == t_type)[:, 0] for t_type in trial_types]
    return t_type_ind, trial_types

def z_score(X):
    # X: ndarray, shape (n_features, n_samples)
    ss = StandardScaler(with_mean=True, with_std=True)
    Xz = ss.fit_transform(X.T).T
    return Xz


def trialAveragedPCA(trialList, t_type_ind, trial_types, n_components):
    """
    A form of PCA that finds principal components across time bins around the time of a trial
    First computes average of trials of each type, then reduces dimensions
    Returns a 3D array with the average population activity for each component for each trial type
    """
    trial_averages = []
    trial_size = trialList[0].shape[1]
    for ind in t_type_ind:
        trial_averages.append(np.array(trialList)[ind].mean(axis=0))
    Xa = np.hstack(trial_averages)
    Xa = z_score(Xa) #Xav_sc = center(Xav)
    pca = PCA(n_components=n_components)
    Xa_p = pca.fit_transform(Xa.T).T
    pcs = np.zeros((n_components, 10, 2))
    for comp in range(n_components):
        for kk, type in enumerate(trial_types):
            x = Xa_p[comp, kk * trial_size :(kk+1) * trial_size]
            x = gaussian_filter1d(x, sigma=3)
            pcs[comp, :, kk] = x
    return pcs

def getUnitDepth(h5file, premotorUnits, visualUnits, visuomotorUnits, depthDict=None):
    """
    Function that returns the coordinates for each unit in a recording & a list of identities for easy indexing
    """
    session = AnalysisObject(h5file)
    points = session.load('nptracer/points')
    population = session._population()
    if depthDict is None:
        depthDict = {identity:[] for identity in ['premotor', 'visual', 'visuomotor']}
    for i, unit in enumerate(population):
        depth = points[i, 2]
        if unit.cluster in premotorUnits:
            depthDict['premotor'].append(depth)
        elif unit.cluster in visualUnits:
            depthDict['visual'].append(depth)
        elif unit.cluster in visuomotorUnits:
            depthDict['visuomotor'].append(depth)
    return depthDict

def getUnitCoords(h5file, premotorUnits, visualUnits, visuomotorUnits, coordDict=None, points=None):
    """
    Function that returns the coordinates for each unit in a recording & a list of identities for easy indexing
    """
    session = AnalysisObject(h5file)
    if points is None:
        points = session.load('nptracer/points')
    population = session._population()
    if coordDict is None:
        coordDict = {identity:[] for identity in ['premotor', 'visual', 'visuomotor']}
    for i, unit in enumerate(population):
        x = points[i, 1]
        y = points[i, 2]
        coords = [x, y]
        if unit.cluster in premotorUnits:
            coordDict['premotor'].append(coords)
        elif unit.cluster in visualUnits:
            coordDict['visual'].append(coords)
        elif unit.cluster in visuomotorUnits:
            coordDict['visuomotor'].append(coords)
    return coordDict

def ROCpreference(a, b, num_repeats):
    """
    """
    numThreshActual = 1000
    numThreshPermuted = 50
    minA = np.min(a)
    minB = np.min(b)
    maxA = np.max(a)
    maxB = np.max(b)
    if minA <= minB:
        minFR = minA - 0.001
    elif minB < minA:
        minFR = minB - 0.001
    if maxA >= maxB:
        maxFR = maxA + 0.001
    elif maxB > maxA:
        maxFR = maxB + 0.001
    thresholds = np.linspace(minFR, maxFR, num=numThreshActual) 
    #icreates an array from min to max with step of numThresh 
    # x-coordinates of ROC curve
    #these are chatGPT but it seems to make sense
    probALargerThanThresh = np.sum(np.tile(a, (numThreshActual, 1)).T > np.tile(thresholds, (len(a), 1)), axis=0, keepdims=True) / len(a)
    # y-coordinates of ROC curve
    probBLargerThanThresh = np.sum(np.tile(b, (numThreshActual, 1)).T > np.tile(thresholds, (len(b), 1)), axis=0, keepdims=True) / len(b)
    probALargerThanThresh = np.fliplr(probALargerThanThresh)
    probBLargerThanThresh = np.fliplr(probBLargerThanThresh)
    rocArea = np.sum(np.diff(probALargerThanThresh) * 
                  ((probBLargerThanThresh[:, :-1] + probBLargerThanThresh[:, 1:]) / 2))
    pref = 2 * (rocArea - 0.5)
    max_length = max(len(a), len(b))
    a_padded = np.pad(a, (0, max_length - len(a)), mode='constant', constant_values=0)
    b_padded = np.pad(b, (0, max_length - len(b)), mode='constant', constant_values=0)
    permutedFR, I = randmat(np.tile(np.hstack([a_padded, b_padded]), (num_repeats, 1)).T, 1);
    permutedA = permutedFR[:len(a), :]
    permutedB = permutedFR[len(a):, :]
    thresholdsPermuted = np.linspace(minFR, maxFR, num=numThreshPermuted)
    replicated_permuted_a = np.repeat(permutedA[:, :, np.newaxis], len(thresholdsPermuted), axis=2)
    reshaped_thresholds = thresholdsPermuted[np.newaxis, np.newaxis, :]
    comparison = replicated_permuted_a > reshaped_thresholds
    probPermutedALargerThanThresh = np.sum(comparison, axis=0) / permutedA.shape[0]
    replicated_permuted_b = np.repeat(permutedB[:, :, np.newaxis], len(thresholdsPermuted), axis=2)
    reshaped_thresholdsb = thresholdsPermuted[np.newaxis, np.newaxis, :]
    comparisonb = replicated_permuted_b > reshaped_thresholdsb
    probPermutedBLargerThanThresh = np.sum(comparisonb, axis=0) / permutedB.shape[0]
    probPermutedALargerThanThresh = np.squeeze(probPermutedALargerThanThresh)
    probPermutedBLargerThanThresh = np.squeeze(probPermutedBLargerThanThresh)
    probPermutedALargerThanThresh = np.fliplr(probPermutedALargerThanThresh)
    probPermutedBLargerThanThresh = np.fliplr(probPermutedBLargerThanThresh)
    rocPermutedArea = np.sum(np.diff(probPermutedALargerThanThresh, axis=1) * 
                  ((probPermutedBLargerThanThresh[:, :-1] + probPermutedBLargerThanThresh[:, 1:]) / 2), axis=1)
    prefPermuted = 2 * (rocPermutedArea - 0.5)
    try:
        tmp = np.where(pref > sorted(prefPermuted))[0][-1] / num_repeats
    except:
        tmp = 0
    if tmp > 0.5:
        pVal = 1 - tmp;
    else:
        pVal = tmp;
    return pref, pVal
