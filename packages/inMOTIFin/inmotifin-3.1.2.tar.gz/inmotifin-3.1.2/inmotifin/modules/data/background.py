""" Data class for backgrounds """
from typing import Dict, List
from dataclasses import dataclass, field
import numpy as np


@dataclass
class Backgrounds:
    """ Class for keeping track of backgrounds

    Class parameters
    ----------------
    backgrounds: Dict[str, str]
        Dictionary of background IDs and sequences
    b_alphabet: str
        Background alphabet, default is "ACGT"
    b_alphabet_prior: np.ndarray
        Background alphabet prior probabilities
    background_ids: List[str]
        List of background IDs (automatically extracted from \
        background dictionary)
    """
    backgrounds: Dict[str, str]
    b_alphabet: str
    b_alphabet_prior: np.ndarray
    background_ids: List[str] = field(init=False)

    def __post_init__(self):
        """ Define background ids as a list """
        self.background_ids = sorted(self.backgrounds.keys())
