import os
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
from matplotlib import colors
from matplotlib.colors import LogNorm
from heputl.utils import preprocessing as prep



# *********************************************************** #
#                         2D histograms                       #
# *********************************************************** #

def plot_2feature_2D_hist(x, y, xlabel='x', ylabel='y', label=None, title='2dhist', plot_name='2dhist', fig_dir=None, axlim=False):

    # Load CMS style sheet
    #plt.style.use(hep.style.CMS)

    # setup colormap for 2dhist
    cmap = cm.get_cmap('Blues')
    xc = np.linspace(0.0, 1.0, 150)
    color_list = cmap(xc)
    color_list = np.vstack((color_list[0], color_list[35:])) # keep white, drop light colors 
    my_cm = colors.ListedColormap(color_list)

    fig = plt.figure(figsize=(8, 8))
    x_min, x_max = np.min(x), np.max(x)
    y_min, y_max = np.min(y), np.max(y)
    x_top = np.percentile(x, 99.999) if axlim else x_max
    y_top = np.percentile(y, 99.999) if axlim else y_max
    ax_range = ((x_min * 0.9,x_top), (y_min * 0.9,y_top))
    plt.hist2d(x, y, range=ax_range, norm=(LogNorm()), bins=200, cmap=my_cm, cmin=0.001)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    #plt.title('quantile cuts' + title_suffix)
    plt.colorbar()
    leg = plt.legend(loc='best', title=title, fontsize=14, title_fontsize=17,frameon=False)
    plt.draw()
    if fig_dir:
        fig.savefig(os.path.join(fig_dir, plot_name+'.png'), bbox_inches='tight')
    plt.show()
    plt.close(fig)




def plot_hist_2d(x, y, xlabel='x', ylabel='y', title='histogram', plot_name='hist2d', fig_dir=None, legend=[], \
    ylogscale=True, normed=True, ylim=None, legend_loc='best', xlim=None, clip_outlier=False, fig_format='.pdf'):
    
    if clip_outlier:
        x,y = prep.clip_outlier(x), prep.clip_outlier(y)

    fig = plt.figure()
    ax = plt.gca()
    im = plot_hist_2d_on_axis( ax, x, y, xlabel, ylabel, title )
    fig.colorbar(im[3])
    plt.tight_layout()
    if fig_dir:
        plt.savefig(os.path.join(fig_dir,plot_name+fig_format))
    plt.show()
    plt.close(fig)
    return ax
    
    
def plot_hist_2d_on_axis(ax, x, y, xlabel, ylabel, title):
    im = ax.hist2d(x, y, bins=100, norm=colors.LogNorm())
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    return im



def plot_2feature_isolines_for_2samples(sample_A:np.ndarray, sample_B:np.ndarray, sample_names:list[str], xlabel:str, ylabel:str, \
										weights_A:np.ndarray=None, weights_B:np.ndarray=None, title_suffix:str=None, filename_suffix:str=None, fig_dir:str='fig', contour_labels:bool=False):
    """plot isoline correlation plots in 2 feature plane for two samples (overlayed)
    
    Args:
        sampleA (np.ndarray): first sample of dimension [N x 2] (number samples x 2 features)
        sampleB (np.ndarray): second sample of dimension [N x 2] (number samples x 2 features)
        title_suffix (None, optional): add to title
        filename_suffix (None, optional): add to filename
        fig_dir (str, optional): plot destination
        contour_labels (bool, optional): show isoline levels
    """
    
    bins = 70
    heatmaps_A, xedges_A, yedges_A = np.hist2d(sample_A[:, 0], sample_A[:, 1], weights=weights_A, bins=bins, normed=True)
    heatmaps_B, xedges_B, yedges_B = np.hist2d(sample_B[:, 0], sample_B[:, 1], weights=weights_B, bins=bins, normed=True)

    min_hist_val = min(np.min(heatmaps_A[heatmaps_A > 0]), np.min(heatmaps_B[heatmaps_B > 0]))  # find min value for log color bar clipping zero values
    max_hist_val = max(np.max(heatmaps_A), np.max(heatmaps_B))

    extent = [min(np.min(xedges_A), np.min(xedges_B)), max(np.max(xedges_A), np.max(xedges_B)), \
              min(np.min(yedges_A), np.min(yedges_B)), max(np.max(yedges_A), np.max(yedges_B))]


    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(9, 9))
    # make dark controur lines
    levels_n = 7
    colors_A = [mpl.colors.rgb2hex(cm.get_cmap('Blues')(int(i))) for i in np.linspace(60, 320, levels_n)]
    colors_B = [mpl.colors.rgb2hex(cm.get_cmap('Oranges')(int(i))) for i in np.linspace(60, 320, levels_n)]

    # plot contours
    cont_A = ax.contour(heatmaps_A.T, cmap=cm.get_cmap('Blues')) #, norm=colors.LogNorm(), colors=colors_A, extent=extent, levels=levels_n)
    cont_B = ax.contour(heatmaps_B.T, cmap=cm.get_cmap('Oranges')) #, norm=colors.LogNorm(), colors=colors_B, extent=extent, levels=levels_n)
    if contour_labels:
        ax.clabel(cont_A, colors='k', fontsize=5.)
        ax.clabel(cont_B, colors='k', fontsize=5.)

    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
        
    # fig.colorbar(cont_A, ax=axs.flat[-1])
    # fig.colorbar(cont_B, ax=axs.flat[-1])
        
    plt.legend([cont_A.collections[0], cont_B.collections[0]], sample_names, loc='center')
    plt.tight_layout()
    fig.savefig(os.path.join(fig_dir, '_'.join(filter(None, ['2D_contour', filename_suffix, '.png']))))
    plt.close(fig)