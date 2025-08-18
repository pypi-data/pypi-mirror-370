""" Data class for motifs """
from typing import Dict, List
from dataclasses import dataclass, field
import numpy as np


@dataclass
class Motifs:
    """ Class for keeping track of motifs

    Class parameters
    ----------------
    motifs: Dict[str, np.ndarray]
        Dictionary of motif IDs and arrays
    alphabet: str
        Alphabet of motifs
    alphabet_revcomp_pairs: Dict[str, str]
        Reverse complementary pairs of alphabet, \
        e.g. {"A": "T", "C": "G", "T": "A", "G": "C"}
    motif_ids: List[str]
        List of motif IDs (automatically extracted from motif dictionary)
    """
    motifs: Dict[str, np.ndarray]
    alphabet: str
    alphabet_revcomp_pairs: Dict[str, str]
    motif_ids: List[str] = field(init=False)

    def __post_init__(self):
        """ Check input data and define motif ids as a list """
        self.check_alphabet()
        self.motif_ids = list(self.motifs.keys())

    def check_alphabet(self):
        """ Make sure that the correct number of letters are provided """
        mismatched = ""
        for motif_id, motif_arr in self.motifs.items():
            if motif_arr.shape[1] != len(self.alphabet):
                mismatched += f"{motif_id}:\nMotif width: {motif_arr.shape[1]}"
                mismatched += f", alphabet length: {len(self.alphabet)}\n\n"
        if len(mismatched) > 0:
            full_msg = "Motif shape should match alphabet.\n"
            full_msg += mismatched
            raise AssertionError(full_msg)
