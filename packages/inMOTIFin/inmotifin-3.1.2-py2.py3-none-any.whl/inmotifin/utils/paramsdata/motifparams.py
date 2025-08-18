""" Data storage for motif parameters """
from typing import List, Dict
from dataclasses import dataclass
import numpy as np


@dataclass
class MotifParams:
    """ Class for keeping track of parameters for motifs

    Class parameters
    ----------------
    dirichlet_alpha: np.ndarray
        Dirichlet prior for motif probabilities, default is uniform
    number_of_motifs: int
        Number of motifs to generate, default is 10
    length_of_motifs_min: int
        Minimum length of motifs, default is 5
    length_of_motifs_max: int
        Maximum length of motifs, default is None, if not set \
        all motifs will have the same length as length_of_motifs_min
    m_alphabet: List[str]
        Motif alphabet, default is "ACGT"
    m_alphabet_pairs: Dict[str, str]
        Motif alphabet pairs for complementary bases, default is \
        {"A": "T", "C": "G", "T": "A", "G": "C"}
    motif_files: List[str]
        List of motif file(s) to use, default is empty
    jaspar_db_version: str
        Release name of JASPAR database version to use when Jaspar IDs are \
        provided in the motif file(s) and fetched from JASPAR database via \
        pyJASPAR. For futher information see pyJASPAR's documentation. \
        Example value: 'JASPAR2024' Default: ``None``
    """
    dirichlet_alpha: np.ndarray
    number_of_motifs: int
    length_of_motifs_min: int
    length_of_motifs_max: int
    m_alphabet: List[str]
    m_alphabet_pairs: Dict[str, str]
    motif_files: List[str]
    jaspar_db_version: str

    def __post_init__(self):
        """ Set default values for parameters if not provided and \
            validate them
        """
        if self.dirichlet_alpha is None:
            self.dirichlet_alpha = [1, 1, 1, 1]
        if self.number_of_motifs is None:
            self.number_of_motifs = 10
        if self.length_of_motifs_min is None:
            self.length_of_motifs_min = 5
        if self.length_of_motifs_max is None:
            self.length_of_motifs_max = self.length_of_motifs_min
        else:
            assert self.length_of_motifs_min <= self.length_of_motifs_max, \
                "length_of_motifs_min (default=5) should not be more than \
                length_of_motifs_max"
        if self.m_alphabet is None:
            self.m_alphabet = "ACGT"
        if self.m_alphabet_pairs is None:
            self.m_alphabet_pairs = {"A": "T", "C": "G", "T": "A", "G": "C"}
        assert len(self.dirichlet_alpha) == len(self.m_alphabet), \
            "dirichlet_alpha should have the same length as m_alphabet"
