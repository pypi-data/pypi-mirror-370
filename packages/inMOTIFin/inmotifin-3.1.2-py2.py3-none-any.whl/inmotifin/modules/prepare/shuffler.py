"""Class to shuffle sequences
author: Kata Ferenc
email: katalitf@uio.no
"""
from typing import Dict
import numpy as np


class Shuffler():
    """Class to shuffle background sequences

    Class parameters
    ----------------
    number_of_shuffle: int
        The number of new sequences to be created from an \
        existing one by shuffling it
    rng: np.random.Generator
        Random generator for permuting letters
    """

    def __init__(
            self,
            number_of_shuffle: int,
            rng: np.random.Generator) -> None:
        """ Initialize background reader

        Parameters
        ----------
        number_of_shuffle: int
            The number of new sequences to be created from an \
            existing one by shuffling it
        rng: np.random.Generator
            Random generator for permuting letters
        """
        self.number_of_shuffle = number_of_shuffle
        self.rng = rng

    def shuffle_seq_random_nucleotide(
            self,
            backgrounds: Dict[str, str]) -> Dict[str, str]:
        """Randomly shuffle each letter in the previously read sequences, \
            adding new sequence entries

        Parameters
        ----------
        backgrounds: Dict[str, str]
            Dictionary of backgrounds to update

        Return
        ------
        shuffled: Dict[str, str]
            Dictionary of shuffled backgrounds
        """
        shuffled = {}
        for seq_id, seq in backgrounds.items():
            for shuffle_iter in range(self.number_of_shuffle):
                shuffled_seq_id = seq_id + "_shuffled" + \
                    str(shuffle_iter + 1)
                char_to_list = list(seq)
                shuffled_seq = ''.join(self.rng.permutation(char_to_list))
                shuffled[shuffled_seq_id] = shuffled_seq
        return shuffled
