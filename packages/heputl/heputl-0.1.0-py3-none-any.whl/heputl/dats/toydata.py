import numpy as np

def samples_from_multivariate_multimodal_gaussian(mus: list | np.ndarray, covs: list | np.ndarray, N_samples: int = 100) -> np.ndarray:

    # set up distribution

    N_dims = len(mus[0])
    N_modes = len(mus)

    mixtures = [scipy.stats.multivariate_normal(mus[i], covs[i]) for i in range(N_modes)]

    # generate samples

    pick_mode = np.random.choice(N_modes, N_samples)
    N_samples_per_mode = [sum(pick_mode == i) for i in range(N_modes)]

    samples_per_mode = [mixtures[i].rvs(N_samples_per_mode[i]) for i in range(N_modes)]
    samples = np.concatenate(samples_per_mode)
    np.random.shuffle(samples)

    return samples
