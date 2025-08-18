"""Utility functions related to calculations"""
import numpy as np


def normalize_array(my_array: np.ndarray) -> np.ndarray:
    """ Normalize the values in an array to sum to 1"""
    motif_base_freq = my_array / sum(my_array)
    return motif_base_freq


def convert_pfm_to_ppm(pfm: np.ndarray) -> np.ndarray:
    """ Convert position frequency matrix to position \
        probability matrix

    Parameters
    ----------
    pfm: np.ndarray
        A single motif in position frequency matrix format \
        2-D numpy array

    Return
    ------
    ppm: np.ndarray
        A single motif in position probability matrix format
    """
    ppm = []
    for row in pfm:
        ppm.append(normalize_array(row))
    return np.array(ppm)
