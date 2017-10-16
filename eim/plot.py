from pylab import *
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib as mpl
mpl.rcParams['interactive'] = True
from matplotlib.colors import *
from scipy import interpolate as inp

from .common import setVariable


def cmapDiscretize(cmap, N):
    """
    Return a discrete colormap from the continuous colormap cmap.
        cmap: colormap instance, eg. cm.jet. 
        N: Number of colors.

    Example
        x = resize(arange(100), (5, 100))
        djet = cmapDiscretize(cm.jet, 5)
        imshow(x, cmap=djet)
    """
    cdict = cmap._segmentdata.copy()
    colors_i = np.linspace(0, 1., N)
    indices = np.linspace(0, 1., N + 1)
    for key in ('red', 'green', 'blue'):
        D = np.array(cdict[key])
        I = inp.interp1d(D[:, 0], D[:, 1])
        colors = I(colors_i)
        # Place these colors at the correct indices.
        A = np.zeros((N + 1, 3), float)
        A[:, 0] = indices
        A[1:, 1] = colors
        A[:-1, 2] = colors
        # Create a tuple for the dictionary.
        L = []
        for l in A:
            L.append(tuple(l))
        cdict[key] = tuple(L)
    # Return colormap object.
    return mpl.colors.LinearSegmentedColormap('colormap', cdict, 1024)

def createLinearColors(ncolors, cmap=mpl.cm.jet):
    """
    Create colors by lineary segmenting given colormap (cmap) in n segments
	    -> ncolors : number of colors
	    -> cmap : colormap
    """
    m = cmapDiscretize(cmap, ncolors)
    clrs = []
    each = 1 + 1024 / ncolors
    for i in range(ncolors):
        clrs.append(m(int(i * each))[:3])
    return clrs


def rearangeData(picdim, data):
    """
        Rearanges data containing weights for nice ploting. And add 1 pixel gap between individual weights.
        -> picdim : dimension of subplots (weights of specific neuron), list [height, width]
        -> data : weights matrix (it is reshaped in most plausible quadratic form),
                array([numhid, picdim[0] * picdim[1]])
    """
    data = data.transpose()
    plotind = np.array(range(0, data.shape[1]))
    numhid = plotind.size
    ploth = int(np.floor(np.sqrt(numhid)))
    while numhid % ploth != 0:
        ploth -= 1
    plotw = np.int(numhid / ploth)

    i = 0
    imh = picdim[0]
    imw = picdim[1]
    immat = np.zeros((ploth * (imh + 1) + 1, plotw * (imw + 1) + 1))

    for y in range(1, ploth + 1):
        for x in range(1, plotw + 1):
            if i > plotind.size:
                break
            immat[(y-1)*(imh+1)+2-1 : (y-1)*(imh+1)+imh+1+1-1,
                    (x-1)*(imw+1)+2-1 : (x-1)*(imw+1)+imw+1+1-1] = data[:,plotind[i]].reshape([imh, imw])
            i += 1
    return immat

def showWeights(sampleshape, W, my_cmap=None, cbar=True):
    """
    Plots weights organised in 2D matrix (most plausible quadratic form).
        -> sampleshape : shape of sample, list [height, width]
        -> W : weight matrix, array([numhid, numvis]), numvis = sampleshape[0]*sampleshape[1]
        -> my_cmap : colormap (if empty list use default colormap)
        -> cbar : if True show colorbar
    """
    fig = plt.figure(figsize=(8, 8))
    plt.axis('off')
    mat = rearangeData(sampleshape, 1 + W)
    cmap = my_cmap if my_cmap else mpl.cm.gray_r
    im = plt.imshow(mat, interpolation='nearest', cmap=my_cmap)

    if cbar:
        fig.colorbar(im)
    plt.draw()
    plt.show()


# returns for each time_ms in times_ms which bar patterns are active at that time
def makeBars(times_ms, pd, patlen):
    nbars = len(times_ms)
    bars = []

    for i, time_ms in enumerate(times_ms):
        bars.append([])
        for k in pd.keys():
            for t in pd[k]:
                if time_ms >= t and time_ms <= t + patlen[k]:
                    bars[i].append(k)
                    break
    return bars


# returns for each time_ms in times_ms a epsp traces from all bar patterns that are active at that time
def makeEpspBars(times_ms, train, pd, patlen, dx, dy, EPSP):
    nbars = len(times_ms)
    bars = np.zeros((nbars, dx, dy))

    EPSPduration_ms = int(EPSP['duration']*1000)
    for i, tajm_ms in enumerate(times_ms):
        epsptrain = train.convertToEPSP2(EPSP, tajm_ms - EPSPduration_ms, tajm_ms)
        print(epsptrain.shape)
        bars[i, :, :]=epsptrain[:, -1].reshape([dx, dy])
    return bars


def markPatterns(ax, patterninds, colors, pd, patlen, start, end, linewidth, yoffset, ydist, xshorten):
    """
    Draw a colored bars representing different patterns of sample on top of plot
        -> ax : ax of figure, where to plot
        -> patterninds : list of pattern IDs we are interested in
        -> colors : list of colors, for each pattern one (modulo operation)
        -> samples : samples we want to mark! (list of TSample class)
        -> start : start time of plot in timestep
        -> end : end time of plot in timesteps
        -> linewidth : width of colored bar
    """
    # patterninds and colors have to have same dimensions
    colors = setVariable(colors, len(patterninds))
    alpha = 1.
    for ind, ID in enumerate(patterninds):
        st = pd[ID] # should be sorted
        length = patlen[ID]
        for t in st:
            starttime = max(start, t)
            endtime = min(end, t + length)
            if starttime < endtime:
                color = colors[ind]

                # new
                y = yoffset + ind * ydist
                xmin = starttime + xshorten  # make it a bit smaller to separte close ones
                xmax = endtime - 1 - xshorten 
                # new

                bkg = np.ones(3)  # white bkg
                ncolor = np.array(color) * alpha + bkg * (1 - alpha)

                #ax.bar(starttime, 0.9, endtime - starttime, ID - 1, color=ncolor, edgecolor=ncolor)
                ax.plot([xmin, xmax], [y,y], linewidth = linewidth, color=ncolor)
				
    #ax.set_ylim(-0.5, max(patterninds))
    ax.set_ylim(0, max(patterninds) * ydist + yoffset)

    ax.set_xlim(start, end)
    plt.draw()


def showTrain(ax, spikes, start, end, colorchannel=['b'], marker='|', size=2, yaxlabel = 'Neuron #', resolution='s', bkgcolorchannel=False):
    """
    Show spike train with colored channels (corresponding to which pattern it has highest correlation).
        -> ax : ax of figure, where to plot
        -> spikes : list of spikes per channel
        -> start : start time of plot in timestep
        -> end : end time of plot in timestep
        -> colorchannel : color for each channel (default is black, modulo operation)
        -> marker : marker used to represent spike
        -> size : size of marker
    """

    if resolution == 's':
        fac=1000.  # convert to ms
    else:
        fac=1.

    nchannels = len(spikes)
    colors = setVariable(colorchannel, nchannels)
    # create train holder for specific range
    tr = []
    # filter spikes
    for ch in range(nchannels):
        tr.append([])
        for sp in spikes[ch]:
            if sp * fac >= start and sp * fac <= end:
                tr[ch].append(sp * fac)
    lenghts = np.zeros(nchannels)
    for nch, ch in enumerate(tr):
        x = []
        y = []
        for sp in ch:
            # add jitter on top - PCSIM uses continuous time with discrete steps
            x.append(sp - 0.5 + np.random.rand())  
            y.append(nch)
        if bkgcolorchannel:
            ax.plot(x, y, marker=marker, linestyle='None', color='k', markeredgecolor='k', markeredgewidth = 1., markersize=size)
            alpha = 0.2
            color = np.array(colors[nch])
            ncolor = color * alpha + np.ones(3) * (1. - alpha)
            ax.bar(start, 1, end - start, nch, color=ncolor, edgecolor=ncolor)
        else:
            ax.plot(x, y, marker=marker, linestyle='None', color=colors[nch], markeredgecolor=colors[nch], markeredgewidth=1., markersize=size)

    ax.set_xlim(start, end)
    ax.set_ylim(0, nchannels)
    ax.set_ylabel(yaxlabel)
    plt.draw()	
