""" Sampling from backgrounds """
from typing import List
import numpy as np
from inmotifin.modules.data.background import Backgrounds


class BackgroundSampler:
    """ Class to support sampling functions

    Class parameters
    ----------------
    backgrounds: Backgrounds
        Data class for backgrounds
    rng: np.random.Generator
        Random generator for selecting a background
    """

    def __init__(
            self,
            backgrounds: Backgrounds,
            rng: np.random.Generator) -> None:
        """ Constructor

        Parameters
        -----------
        backgrounds: Backgrounds
            Data class for backgrounds
        rng: np.random.Generator
            Random generator for selecting a background
        """
        self.backgrounds = backgrounds
        self.rng = rng

    def get_background_id(self) -> str:
        """ Get a selected background sequence ID

        Return
        ------
        selected_id: str
            One sequence ID
        """
        selected_id = self.rng.choice(
            a=self.backgrounds.background_ids,
            size=1)[0]
        return selected_id

    def get_single_background(self, selected_id: str) -> str:
        """ Get a selected background sequence

        Parameters
        ----------
        selected_id: str
            The name of the selected sequence

        Return
        ------
        _: str
            One sequence
        """
        return self.backgrounds.backgrounds[selected_id]

    def get_b_alphabet(self) -> str:
        """ Get background alphabet
        """
        return self.backgrounds.b_alphabet

    def get_b_alphabet_prior(self) -> np.ndarray:
        """ Get background alphabet prior
        """
        return self.backgrounds.b_alphabet_prior

    def get_backgrounds(self, num_backgrounds: int) -> List[str]:
        """ Get a list of backgrounds

        Parameters
        ----------
        num_backgrounds: int
            Number of requested backgrounds

        Return
        ------
        selected_backgrounds: List[str]
            List of non-unique comma separated background IDs and sequences
        """
        selected_backgrounds = []
        for _ in range(num_backgrounds):
            background_id = self.get_background_id()
            background_seq = self.get_single_background(
                selected_id=background_id
            )
            selected_backgrounds.append(f"{background_id},{background_seq}")

        return selected_backgrounds
