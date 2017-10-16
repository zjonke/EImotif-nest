import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib as mpl
from matplotlib.colors import *

from eim.plot import showTrain, markPatterns


def plotSTPFig(train, pd, patlen, pg, start, end, pinds, pc, spikesIN_ms, P1_spikesZ_ms, P2_spikesZ_ms, rest_spikesZ_ms, spikesI_ms,  nrntracesP1_P1, nrntracesP1_P2, nrntracesP2_P1, nrntracesP2_P2):
    """
        Plot: 1) input formation: a) green/blue spikes b) nonlinear box c) green & red OU rates d) realizations
              2) patterns marks green/blue
              3) input spikes
              4) selective z spikes
              5) rest z spikes
              6) I spikes
              7) CH analyses
    """

    cm2inch= lambda x: x * 0.393701
    figx = 16  # cm
    figy = 9  # cm

    fig = plt.figure(figsize=(cm2inch(figx),cm2inch(figy)))
    
    #spikesize
    spikesize = 2

    # start layout
    y = figy

    # top space
    dy = 0.25
    y -= dy

    # patterns marks green/blue
    dy = 0.5
    y -= dy
    ax = fig.add_axes([1.5 / figx, y / figy, 14. / figx, dy / figy])
    ax.axis('off')
    markPatterns(ax, pinds, pc, pd, patlen, start, end, linewidth=4, yoffset=0.5, ydist=1., xshorten=10)

    # space
    dy = 0.25
    y -= dy

    # input spikes, 100 nrns
    dy = 2.5
    y -= dy
    ax = fig.add_axes([1.5 / figx, y / figy, 14. / figx, dy / figy])
    ax.set_xticks([])
    ax.set_yticks([1, 100])
    plt.setp(ax.get_xticklabels(), visible=False)
    showTrain(ax, spikesIN_ms, start, end, size=spikesize, colorchannel=['k'], yaxlabel='Inp. neurons', resolution='ms')

    # space
    dy = 0.25
    y -= dy

    # selective z neurons - spikes, 87 & 82 nrns
    dy = 4.22
    y -= dy
    ax = fig.add_axes([1.5 / figx, y / figy, 14. / figx, dy / figy])
    ax.set_xticks([])
    ax.set_yticks([1, len(P1_spikesZ_ms), len(P1_spikesZ_ms) + len(P2_spikesZ_ms)])
    plt.setp(ax.get_xticklabels(), visible=False)
    scolors = [pc[0]] * len(P1_spikesZ_ms) + [pc[1]] * len(P2_spikesZ_ms)
    spikesZ_ms = P1_spikesZ_ms + P2_spikesZ_ms
    showTrain(ax, spikesZ_ms, start, end, size=spikesize, colorchannel=scolors, yaxlabel='Exc. neurons', resolution='ms')


    plt.draw()





