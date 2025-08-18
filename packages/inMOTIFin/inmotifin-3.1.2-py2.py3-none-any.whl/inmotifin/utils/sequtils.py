"""Utility functions related to sequences"""
from typing import List, Dict
import numpy as np


def onehot_to_str(alphabet: List[chr], motif_onehot: List[np.array]) -> str:
    """Convert one-hot encoded motif into a string motif

    Parameters
    ----------
    alphabet: List[chr]
        Allowed characters in the sequence (eg [A, C, G, T] or 'ACGT')
    motif_onehot: List[np.array]
        One-hot encoded motif

    Return
    ------
    motif: str
        Motif in string format
    """
    motif_list = []
    for base in motif_onehot:
        motif_list.append(alphabet[np.where(base == 1)[0][0]])
    motif = "".join(motif_list)
    return motif


def create_reverse_complement(
        alphabet: Dict[chr, chr],
        motif_instance: str) -> str:
    """Translate sequence to its reverse complement. Case sensitive

    Parameters
    ----------
    alphabet: Dict[chr, chr]
        Pairs of characters and their complementary pairs
        e.g. {'A':'T', 'C':'G', 'G':'C', 'T':'A'}
    motif_instance: str
        Motif sequence

    Return
    ------
    revcomp: str
        Reverse complement of motif sequence
    """
    comp_list = []
    for base in str(motif_instance):
        if base not in alphabet.keys():
            raise AssertionError(
                f"{base} is not present in the provided \
                    alphabet {alphabet}")
        comp_list.append(alphabet[base])
    revcomp_list = comp_list[::-1]
    revcomp = "".join(revcomp_list)
    return revcomp


def define_complementary_map_motif_array(
        alphabet: str,
        alphabet_pairs: Dict[str, str]) -> List[int]:
    """Translate index of alphabet letter pair for column permutation

    Parameters
    ----------
    alphabet: str
        Alphabet in the order of motif numpy array columns
    alphabet_pairs: Dict[chr, chr]
        Pairs of characters and their complementary pairs
        e.g. {'A':'T', 'C':'G', 'G':'C', 'T':'A'}

    Return
    ------
    complementary_idx: List[int]
        Index of the partner of the letter
    """
    complementary_map = [
        alphabet.index(
            alphabet_pairs[letter]
            ) for letter in alphabet]
    complementary_idx = np.empty_like(complementary_map)
    complementary_idx[complementary_map] = np.arange(len(complementary_map))
    return complementary_idx


def create_reverse_complement_motif(
        motif: np.ndarray,
        complementary_idx: List[int]) -> np.ndarray:
    """Translate index of alphabet letter pair

    Parameters
    ----------
    motif: np.ndarray
        PPM of a motif in shape (len, alphabet)
    complementary_idx: List[int]
        Index of the partner of the letter

    Return
    ------
    oriented_motif: np.ndarray
        PPM of a reverse complemented motif in shape (len, alphabet)
    """
    complementary_motif = motif[:, complementary_idx]
    oriented_motif = np.flip(complementary_motif, axis=0)
    return oriented_motif
