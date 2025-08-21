import matplotlib.pyplot as plt
from felsen_analysis.toolkit.process import AnalysisObject
import unit_localizer as ul
import numpy as np
import random

def plotPCA3D(pcs, trial_types, dimensions, stimIndex, saveFig=False):
    """
    Takes PCA output & plots it in 3D
    """
    ax = plt.figure().add_subplot(projection='3d')
    ax.plot(pcs[dimensions[0],:, 0], pcs[dimensions[1],:, 0], pcs[dimensions[2],:, 0], color='deepskyblue', label=trial_types[0])
    ax.plot(pcs[dimensions[0],:, 1], pcs[dimensions[1],:, 1], pcs[dimensions[2],:, 1], color='magenta', label=trial_types[1])
    ax.plot(pcs[dimensions[0],stimIndex, 1], pcs[dimensions[1],stimIndex, 1], pcs[dimensions[2],stimIndex, 1], color='magenta', marker='o')
    ax.plot(pcs[dimensions[0],stimIndex, 0], pcs[dimensions[1],stimIndex, 0], pcs[dimensions[2],stimIndex, 0], color='deepskyblue', marker='o')
    ax.plot(pcs[dimensions[0],0, 0], pcs[dimensions[1],0, 0], pcs[dimensions[2],0, 0], color='k', marker='o')
    ax.plot(pcs[dimensions[0],0, 1], pcs[dimensions[1],0, 1], pcs[dimensions[2],0, 1], color='k', marker='o')

    ax.set_xlabel('PC' + str(dimensions[0]))
    ax.set_ylabel('PC' + str(dimensions[1]))
    ax.set_zlabel('PC' + str(dimensions[2]))
    ax.legend()
    if saveFig == True:
        plt.savefig(f'{trial_types[0]}-{trial_types[1]}-pca3d', format="svg")
    return ax

def plotPETH(h5file, unitList, events, color, start, stop, step, label, saveFig=True, avgOnly=True, fig=None, ax=None):
    """
    Takes ephys & event inputs and plots a basic PETH of each unit with an average
    """
    if fig is None:
        fig, ax = plt.subplots()
    frList = list()
    session = AnalysisObject(h5file)
    population = session._population()
    for unit in population:
        if unit.cluster in unitList:
            t, fr = unit.peth(events, (start, stop), step)
            baseline = np.mean(fr[0:10])
            corrected = fr - baseline
            if avgOnly == False:
                ax.plot(t, corrected, color=color, alpha=0.25)
            frList.append(corrected)
    frAvg = np.mean(frList, axis=0)
    if avgOnly ==True:
        ax.plot(t, frAvg, color=color, label=label)
    else:
        ax.plot(t, frAvg, color=color)

    if saveFig == True:
        plt.savefig(f'{label}-PETH', format="svg")
    return fig, ax

def plotKDE(h5file, unitList, events, color, start, stop, step, label, saveFig=True, avgOnly=True, fig=None, ax=None):
    """
    Takes ephys & event inputs and plots a basic PETH of each unit with an average
    """
    if fig is None:
        fig, ax = plt.subplots()
    frList = list()
    session = AnalysisObject(h5file)
    population = session._population()
    for unit in population:
        if unit.cluster in unitList:
            t, fr = unit.kde(events, (start, stop), step)
            baseline = np.mean(fr[0:10])
            corrected = fr - baseline
            if avgOnly == False:
                ax.plot(t, corrected, color=color, alpha=0.25)
            frList.append(corrected)
    frAvg = np.mean(frList, axis=0)
    if avgOnly ==True:
        ax.plot(t, frAvg, color=color, label=label)
    else:
        ax.plot(t, frAvg, color=color)
    

    if saveFig == True:
        plt.savefig(f'{label}-kde', format="svg")

    return fig, ax

def plotUnitDepth(depthDict, saveFig=True):
    """
    Plots depth of units, color coded by type, across sessions
    """
    fig, ax = plt.subplots(figsize=(4,10))
    plt.scatter([random.random() for d in range(len(depthDict['premotor']))], depthDict['premotor'], color='magenta')
    plt.scatter([random.random() for d in range(len(depthDict['visual']))], depthDict['visual'], color='limegreen')
    plt.scatter([random.random() for d in range(len(depthDict['visuomotor']))], depthDict['visuomotor'], color='blueviolet')
    plt.xlim(-0.5, 1.5)
    plt.ylim(0, 350)
    plt.xticks([])
    ax.invert_yaxis()
    plt.yticks([0, 100, 200, 300], [0, 1, 2, 3])
    ax.tick_params(axis='y', labelsize=18)
    plt.ylabel('Unit Depth (mm)', fontsize=20)
    if saveFig == True:
        plt.savefig(f'unitDepth', format="svg")
    return fig, ax

def plotUnitDepthOverBrain(coordDict, allenFile, saveFig=True):
    """
    Uses 2D coordinates to plot unit location over real brain
    """
    fig, ax = plt.subplots()
    ul.loadAllData(path=allenFile)
    section = ul.VOLUME[900, :, :]
    ax.imshow(np.transpose(section), cmap='Greys', vmin=0, vmax=255)
    for i, point in enumerate(coordDict['premotor']):
        ax.scatter(coordDict['premotor'][i][0] + random.uniform(0, 10), coordDict['premotor'][i][1], color='magenta', s=10)
    for i, point in enumerate(coordDict['visual']):
        ax.scatter(coordDict['visual'][i][0]+ random.uniform(0, 10), coordDict['visual'][i][1], color='limegreen', s=10)
    for i, point in enumerate(coordDict['visuomotor']):
        ax.scatter(coordDict['visuomotor'][i][0]+ random.uniform(0, 10), coordDict['visuomotor'][i][1], color='blueviolet', s=10)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xlim(200, 1000)
    ax.set_ylim(500, 0)
    return fig, ax

def plotRaster(eventTimes, spikeTimes, window, eventType):
    """
    Makes a raster plot for a given unit for a given event type
    """
    L = list()
    for event in eventTimes:
        b1 = event + window[0]
        b2 = event + window[1]
        maskB = np.logical_and(spikeTimes >= b1, spikeTimes < b2)
        b = spikeTimes[maskB] - event
        L.append(b)
    L1 = np.array(L)
    fig, ax = plt.subplots()
    font = {'size' : 15}
    plt.rc('font', **font)
    plt.gca().invert_yaxis()
    for rowIndex, row in enumerate(L1):
        x = row
        y0 = rowIndex - 3
        y1 = rowIndex + 3
        ax.vlines(x, y0, y1, color='k', lw=2)
    ax.set_ylabel('Trial', fontsize=20)
    ax.set_xlabel(f'Time from {eventType} (sec)', fontsize=20)
    ax.tick_params(axis='x', labelsize=18)
    ax.tick_params(axis='y', labelsize=18)
    fig.set_figheight(10)
    fig.set_figwidth(6)

    return fig, ax

