import matplotlib.pyplot as plt
import os
import numpy as np
import mplhep as hep
import matplotlib.cm as cm

from heputl.utils import string_constants as stco
from heputl.utils import preprocessing as prep


plt.rcParams['axes.formatter.min_exponent'] = 1


def get_bg_idx(sample_names, bg_name):

    if bg_name is not None:
        return [i for (i,s) in enumerate(sample_names) if bg_name in s][0]
    else:
        return -1


# *********************************************************** #
#                         1D histograms                       #
# *********************************************************** #



def plot_feature_hist_for_n_samples(data:list|np.ndarray, sample_names:list[str], weights:list|np.ndarray=None, bins:int=100, xlabel:str='x', ylabel:str='fraction events', clip_outlier=False, normed=True, \
    ylogscale=True, xlim=None, plot_name='feature_hist', fig_dir=None, fig_format='.pdf', fig_size=(6.5,5), bg_name=None, histtype_bg='stepfilled', \
    show_plt=False, legend_outside=True, palette=stco.default_palette, sci_xax:bool=True) -> None:
    '''
    plots single feature distribution for multiple samples as 1D histogram
    :param data: list of J ndarrays of each N feature values
    :param bg_name: if not None, one sample will be treated as background and plotted in histtype_bg style
    '''

    # if only a single sample is passed in (n=1)
    if type(data) is not list: data = [data]
    if weights is not None and type(weights) is not list: weights = [weights]
    if type(sample_names) is not list: sample_names = [sample_names]

    # if one sample is to be treated as background sample
    bg_idx = get_bg_idx(sample_names, bg_name)

    plt.style.use(hep.style.CMS)

    fig = plt.figure(figsize=fig_size)
    if ylogscale:
        plt.yscale('log')

    for i, (dat, ww, col) in enumerate(zip(data, weights or [None]*len(data), palette)):
        if clip_outlier:
            idx = prep.is_outlier_percentile(dat)
            dat = dat[~idx]
            ww = ww[~idx] if ww else None
        if i == bg_idx:
            plt.hist(dat, weights=ww, bins=bins, density=normed, alpha=0.5, histtype=histtype_bg, label=sample_names[i], color=col, lw=1.5)
        else:
            plt.hist(dat, weights=ww, bins=bins, density=normed, alpha=1.0, histtype='step', label=sample_names[i], color=col, lw=1.5)

    if xlim:
        plt.xlim(xlim)
    plt.grid()
    plt.ylabel(ylabel, fontsize=16)
    plt.xlabel(xlabel, fontsize=16)
    plt.gca().tick_params(axis='both', which='major', labelsize=14)
    plt.gca().tick_params(axis='both', which='minor', labelsize=14)
    # set magnitude tick label to small size
    if sci_xax:
        plt.gca().ticklabel_format(style='scientific', scilimits=(-1, 2), axis='x',useMathText=True)
    text = plt.gca().xaxis.get_offset_text() # Get the text object
    text.set_size(14)
    text.set_x(0.1)
    if legend_outside:
        handles, labels = plt.gca().get_legend_handles_labels()
        lgd = fig.legend(handles, labels, bbox_to_anchor=(0.5,-0.1), loc="lower center", ncol=len(data), labelspacing=0.8, fontsize=16)
        bbox_extra_artists = (lgd,)
    else:
        plt.legend(loc='best', fontsize=15)
        bbox_extra_artists = None
    plt.tight_layout()
    if show_plt:
        plt.show()
    if fig_dir:
        print('writing figure to ' + os.path.join(fig_dir, plot_name + fig_format))
        fig.savefig(os.path.join(fig_dir, plot_name + fig_format), bbox_extra_artists=bbox_extra_artists, bbox_inches='tight')
    plt.close(fig)




# *********************************************************** #
#                         1D graphs                           #
# *********************************************************** #


def plot_function_graph_for_n_samples(x_dat:list|np.ndarray, y_dat:list|np.ndarray, sample_names:list[str], xlabel:str='x', ylabel:str='y', plot_name='feature_hist', \
    scatter=False, fig_dir=None, fig_format='.pdf', fig_size=(5.5,4), show_plt=False, xlogscale=False, ylogscale=False, legend_outside=False, palette:list=stco.default_palette) -> None:

    """Plot a function graph for n samples.  

    """

    if type(x_dat) is not list: x_dat = [x_dat]
    if type(y_dat) is not list: y_dat = [y_dat]
    if len(x_dat) is not len(y_dat): x_dat = x_dat*len(y_dat)
    if type(sample_names) is not list: sample_names = [sample_names]

    plt.style.use(hep.style.CMS)

    fig = plt.figure(figsize=fig_size)
    if ylogscale:
        plt.yscale('log')
    if xlogscale:
        plt.xscale('log')

    for i, (xx, yy, col) in enumerate(zip(x_dat, y_dat, palette)):
        if scatter:
            plt.scatter(xx, yy, label=sample_names[i], color=col, lw=1.5, s=2)
        else:
            plt.plot(xx, yy, label=sample_names[i], color=col, lw=1.5)

    plt.grid()
    plt.ylabel(ylabel, fontsize=16)
    plt.xlabel(xlabel, fontsize=16)
    plt.gca().tick_params(axis='both', which='major', labelsize=14)
    plt.gca().tick_params(axis='both', which='minor', labelsize=14)
    # set magnitude tick label to small size
    if not xlogscale:
        plt.gca().ticklabel_format(style='scientific', scilimits=(-1, 2), axis='x',useMathText=True)
        text = plt.gca().xaxis.get_offset_text() # Get the text object
        text.set_size(14)
        text.set_x(0.1)
    if legend_outside:
        handles, labels = plt.gca().get_legend_handles_labels()
        lgd = fig.legend(handles, labels, bbox_to_anchor=(0.5,-0.1), loc="lower center", ncol=len(y_dat), labelspacing=0.8, fontsize=16)
        bbox_extra_artists = (lgd,)
    else:
        plt.legend(loc='best', fontsize=15)
        bbox_extra_artists = None
    plt.tight_layout()
    if show_plt:
        plt.show()
    if fig_dir:
        print('writing figure to ' + os.path.join(fig_dir, plot_name + fig_format))
        fig.savefig(os.path.join(fig_dir, plot_name + fig_format), bbox_extra_artists=bbox_extra_artists, bbox_inches='tight')
    plt.close(fig)

