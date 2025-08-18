""" Data storage for background parameters """
from typing import List
from dataclasses import dataclass
import numpy as np


@dataclass
class BackgroundParams:
    """ Class for keeping track of parameters for background

    Class parameters
    ----------------
    b_alphabet: str
        Background alphabet, default is "ACGT"
    b_alphabet_prior: np.ndarray
        Background alphabet prior probabilities, default is uniform
    number_of_backgrounds: int
        Number of backgrounds to generate, default is 100
    length_of_backgrounds: int
        Length of each background sequence, default is 50
    background_files: List[str]
        List of background files to use, default is empty
    shuffle: str
        Type of shuffling to apply to the backgrounds, default is "none"
    number_of_shuffle: int
        Number of times to shuffle the backgrounds
    """
    b_alphabet: List[str]
    b_alphabet_prior: np.ndarray
    number_of_backgrounds: int
    length_of_backgrounds: int
    background_files: List[str]
    shuffle: str
    number_of_shuffle: int

    def __post_init__(self):
        """ Set default values for parameters if not provided and \
        validate them
        """
        if self.b_alphabet is None:
            self.b_alphabet = "ACGT"
        if self.b_alphabet_prior is None:
            self.b_alphabet_prior = [0.25, 0.25, 0.25, 0.25]
        assert len(self.b_alphabet_prior) == len(self.b_alphabet), \
            "b_alphabet_prior should have the same length as b_alphabet"
        self.b_alphabet_prior = np.array(self.b_alphabet_prior)
        if self.number_of_backgrounds is None:
            self.number_of_backgrounds = 100
        if self.length_of_backgrounds is None:
            self.length_of_backgrounds = 50
        if self.shuffle is None:
            self.shuffle = "none"
