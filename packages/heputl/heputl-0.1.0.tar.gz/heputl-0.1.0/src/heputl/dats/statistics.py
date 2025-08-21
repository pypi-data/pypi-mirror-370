import numpy as np


# *************************************************************************#
#                           binnings
# *************************************************************************#


def get_expo_bins(n_bins=40, min_val=1200., max_val=6000, bin_centers=True):
    ''' exponentially expanding bin-width '''
    x_shift = 3
    lin_bins = np.linspace(0.,1.,n_bins)
    exp_bins = lin_bins/(np.exp(-lin_bins+x_shift)/np.exp(x_shift-1))
    bins = exp_bins*(max_val-min_val)+min_val
    if bin_centers:
        bins = [(high+low)/2. for low, high in zip(bins[:-1], bins[1:])]
    return np.asarray(bins)


def get_linear_bins(n_bins=40, min_val=1200., max_val=6000, bin_centers=True):
    bins = np.array(np.linspace(min_val, max_val, n_bins).tolist()).astype('float')
    if bin_centers:
        bins = [(high+low)/2. for low, high in zip(bins[:-1], bins[1:])]
    return np.asarray(bins)
