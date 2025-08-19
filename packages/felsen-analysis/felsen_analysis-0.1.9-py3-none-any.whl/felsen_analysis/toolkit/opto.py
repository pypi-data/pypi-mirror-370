import os
import glob
import numpy as np
import matplotlib.pyplot as plt
from pyopenephys import File
import pandas as pd
from felsen_analysis.toolkit.process import AnalysisObject
from zetapy import zetatest
import spikeinterface.extractors as se
import spikeinterface.preprocessing as spre
import spikeinterface.sorters as sorters
from spikeinterface.core import write_binary_recording
from scipy import stats


def removeArtifacts(basePath, output, mode, optoTimes, ms_before, ms_after, offsets=True):
    """
    Use spike interface's remove_artifacts function to remove artifacts and save out a .dat file that can be kilosorted
    Base path must contain in it the Record Node 101 directory!
    """
    recording = se.OpenEphysBinaryRecordingExtractor(basePath, stream_name=np.str_('Record Node 101#Neuropix-PXI-100.ProbeA-AP'))
    optoTimesTotal = list()
    optoListLabels = list()
    if offsets == True:
        for onset in optoTimes:
            offset = onset + 0.01
            optoTimesTotal.append(onset)
            optoTimesTotal.append(offset)
            optoListLabels.append('onset')
            optoListLabels.append('offset')     
        optoTimesTotal = np.array(optoTimesTotal)
    else:
        optoTimesTotal = np.array(optoTimes)
        for onset in optoTimes:
            optoListLabels.append('onset')
    removed = spre.remove_artifacts(recording, np.around(optoTimesTotal*30000).astype(int), ms_before = ms_before,ms_after = ms_after, list_labels=optoListLabels, mode=mode)
    write_binary_recording(removed, file_paths=[os.path.join(basePath, f'{output}{mode}artifact.dat')], dtype="int16")  # or "int16" depending on your analysis pipeline)
    return

def plotRawNeuropixelsData(t2plot, folderPath, datPath, vmin=None, vmax=None):
    """
    Takes .dat file (raw Neuropixels data) and plots a small section
    Probably not more than 10sec if you don't want to crash your computer :)
    Particularly useful for assessing opto artifacts
    """
    freq = 30_000  # sampling rate placeholder
    file = File(folderPath)
    exp = file.experiments[0]
    rec = exp.recordings[0]
    fs = rec.sample_rate
    file_size = os.path.getsize(datPath)  # in bytes
    channel_count = 384
    total_samples = file_size // (2 * channel_count)  # 2 bytes per int16
    # Memory-map full range
    sig_all = np.memmap(datPath, dtype='int16', mode='r', shape=(total_samples, channel_count))
    # Slice for your chosen window
    start_idx = int(t2plot[0] * fs)
    end_idx   = int(t2plot[1] * fs)
    sig_window = sig_all[start_idx:end_idx, :]  # shape: (window_duration × channel_count)
    sig = sig_window.T  # shape: (channels × window_duration)
    # Plot analog trace
    n_ch, n_samps = sig.shape
    fig, axs = plt.subplots(figsize=(10, 5))
    im = axs.imshow(sig, aspect='auto', origin='lower', extent=[t2plot[0], t2plot[1], 0, n_ch],cmap='inferno', vmin=vmin, vmax=vmax)
    fig.colorbar(im)
    return fig, axs

def runZetaTestForOpto(h5file, eventTimestamps, responseWindow, latencyMetric):
    """
    ZETA test to check if neurons are responsive to the opto stim
    """
    session = AnalysisObject(h5file)
    population = session._population()
    tOffset = 0 - responseWindow[0]
    responseWindowAdjusted = np.array(responseWindow) + tOffset
    #
    result = np.full([len(population), 3], np.nan)
    unitIndex = 0
    for i, unit in enumerate(population):
        p, dZeta, dRate = zetatest(
            unit.timestamps,
            eventTimestamps - tOffset,
            dblUseMaxDur=np.max(responseWindowAdjusted),
            tplRestrictRange=responseWindowAdjusted,
            boolReturnRate=True,
        )
        allLatencies = dZeta['vecLatencies']

        # NOTE: Sometimes this returns a list
        if type(allLatencies) == list:
            allLatencies = np.array(allLatencies)

        # NOTE: Sometimes this returns a 2D array (single column)
        if type(allLatencies) == np.ndarray and len(allLatencies.shape) == 2:
            allLatencies = np.ravel(allLatencies)

        #
        if latencyMetric == 'zenith':
            tLatency = round(allLatencies[0] - tOffset, 3)
        elif latencyMetric == 'peak':
            tLatency = round(allLatencies[2] - tOffset, 3)
        elif latencyMetric == 'onset':
            tLatency = round(allLatencies[3] - tOffset, 3)
        else:
            tLatency = np.nan
        result[unitIndex, :] = [unitIndex, tLatency, p]
        unitIndex = unitIndex + 1
        
        #
    session.save(f'zeta/optostim/p', result[:, 2])
    session.save(f'zeta/optostim/latency', result[:, 1])
    return

def defineOptoPopulation(h5file, clusterFile, zetaOpto=None, ampCutoff=None, presenceRatio=None, firingRate=None, isiViol=None, qualityLabels=None):
    """
    This function filters your population of neurons and pulls out opto-responsive neurons based on ZETA test results
    """
    session = AnalysisObject(h5file)
    spikeClustersFile = clusterFile
    uniqueSpikeClusters = np.unique(np.load(spikeClustersFile))
    if zetaOpto is None:
        zetaOpto = session.load('zeta/optostim/p')
    if ampCutoff is None:
        ampCutoff = session.load('metrics/ac')
        presenceRatio = session.load('metrics/pr')
        firingRate = session.load('metrics/fr')
        isiViol = session.load('metrics/rpvr')
        qualityLabels = session.load('metrics/ql')
    optoUnitsZeta = list()
    for index, pVal in enumerate(zetaOpto):
        if pVal < 0.01:
            if qualityLabels is not None and qualityLabels[index] in (0, 1):
                    continue
            if ampCutoff[index] <= 0.1:
                if presenceRatio[index] >= 0.9:
                    if firingRate[index] >= 0.2:
                        if isiViol[index] <= 0.5:
                            unit = uniqueSpikeClusters[index]
                            optoUnitsZeta.append(unit)

    return optoUnitsZeta

def defineOptoPopulationTTest(h5file, clusterFile, optoTimes, ampCutoff=None, presenceRatio=None, firingRate=None, isiViol=None, qualityLabels=None):
    """
    This function uses a t-test to pull out opto-responsive neurons
    """
    session = AnalysisObject(h5file)
    population = session._population()
    spikeClustersFile = clusterFile
    responseWindow = [0.003, 0.008]
    uniqueSpikeClusters = np.unique(np.load(spikeClustersFile))
    if ampCutoff is None:
        ampCutoff = session.load('metrics/ac')
        presenceRatio = session.load('metrics/pr')
        firingRate = session.load('metrics/fr')
        isiViol = session.load('metrics/rpvr')
        qualityLabels = session.load('metrics/ql')
    pList = list()
    clusterList = list()
    for index, unit in enumerate(population):
        real = list()
        fake = list()
        spikeTimes = unit.timestamps
        if qualityLabels is not None and qualityLabels[index] in (0, 1):
                    continue
        if ampCutoff[index] <= 0.1:
            if presenceRatio[index] >= 0.9:
                if firingRate[index] >= 0.2:
                    if isiViol[index] <= 0.5:
                        for time in optoTimes:
                            start = time + responseWindow[0]
                            end = time + responseWindow[1]
                            mask = np.logical_and(spikeTimes > start, spikeTimes < end)
                            response = len(spikeTimes[mask])/0.005
                            real.append(response)
                        for i in range(len(optoTimes)):
                            startFake = np.random.uniform(np.min(optoTimes), np.max(optoTimes))
                            endFake = startFake + 0.005
                            maskFake = np.logical_and(spikeTimes > startFake, spikeTimes < endFake)
                            responseFake = len(spikeTimes[maskFake])/0.005
                            fake.append(responseFake)
                        stat, p = stats.ttest_rel(real, fake, nan_policy='omit')
                        pList.append(p)
                        clusterList.append(unit.cluster)
    return clusterList, pList



