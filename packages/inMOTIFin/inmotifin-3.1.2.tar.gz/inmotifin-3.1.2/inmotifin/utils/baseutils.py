""" Utility functions related to general data transformations """
from typing import Dict, List
import numpy as np


def dict_of_list_to_dict(indict: Dict[str, List[str]]) -> Dict[str, str]:
    """ Convert Dict of list to Dict of single elements

    Parameters
    ----------
    indict: Dict[str, List[str]]
        Input dictionary of lists

    Return
    ------
    outdict: Dict[str, str]
        Output dictionary with modified keys and single element values
    """
    outdict = {}
    for idx, values in indict.items():
        val_counter = 0
        for current_val in values:
            new_idx = idx + "_" + str(val_counter)
            outdict[new_idx] = current_val
            val_counter += 1
    return outdict


def choice_from_dict(
        indict: Dict[str, float],
        size: int,
        rng: np.random.Generator,
        replace: bool = True) -> np.ndarray:
    """ Select from dict of IDs and probabilities

    Parameters
    ----------
    indict: Dict[str, float]
        Input dictionary of IDs and floats
    size: int
        Number of elements to chose
    rng: np.random.Generator
        Random generator for sampling
    replace: bool
        Whether to sample with replacement. Defaults to True

    Return
    ------
    selected_ids: np.ndarray
        Np array of selected elements
    """
    # ensure correct order between two lists
    id_list = []
    prob_list = []
    for myid, prob in indict.items():
        id_list.append(myid)
        prob_list.append(prob)

    selected_ids = rng.choice(
        a=id_list,
        size=size,
        replace=replace,
        p=prob_list)

    return selected_ids


def add_names_to_str(
        seq_list: List[str],
        title: str) -> Dict[str, str]:
    """ Given a title, name sequences

    Parameters
    ----------
    seq_list: List[str]
        List of sequences
    title: str
        Name of the sequences.

    Return
    ------
    named_seq: Dict[str, str]
        Dictionary of IDs and sequences
    """
    named_seq = {}
    for idx, bseq in enumerate(seq_list):
        seq_id = title + "_seq_" + str(idx)
        named_seq[seq_id] = bseq
    return named_seq
