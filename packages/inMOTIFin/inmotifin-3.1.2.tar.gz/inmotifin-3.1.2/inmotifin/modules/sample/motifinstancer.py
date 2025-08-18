""" Generate motif instances from motifs """
from typing import List
import numpy as np
from inmotifin.utils import sequtils
from inmotifin.modules.data.motif import Motifs


class MotifInstancer:
    """ Class to take in motifs and generate \
    the required number of instances

    Class parameters
    ----------------
    motifs: Motifs
        Data class for motifs with names (key) and PPM
    rng: np.random.Generator
        Random generator for multinomial instance sampling
    """

    def __init__(
            self,
            motifs: Motifs,
            rng: np.random.Generator) -> None:
        """ Constructor for motif instance generator

        Parameters
        ----------
        motifs: Motifs
            Data class for motifs with names (key) and PPM
        rng: np.random.Generator
            Random generator for multinomial instance sampling
        """
        self.motifs = motifs
        self.rng = rng

    def get_one_new_instance(
            self,
            motif_index: str) -> str:
        """ Generate exactly one new motif instance

        Parameters
        ----------
        motif_index: str
            ID of the motif from which an instance to be sampled

        Return
        ------
        instance_str: str
            Sequence of a motif instance
        """
        motif = self.motifs.motifs[motif_index]
        l_motif = len(motif)
        instance_onehot = []
        for letter in range(l_motif):
            instance_onehot.append(
                self.rng.multinomial(1, motif[letter]))
        instance_str = sequtils.onehot_to_str(
            alphabet=self.motifs.alphabet,
            motif_onehot=instance_onehot)
        return instance_str

    def sample_instances(
            self,
            motif_idx_list: List[str],
            orientations: List[int]) -> List[str]:
        """ Accessor function for creating new instances

        Parameters
        ----------
        motif_idx_list: List[str]
            List of motif IDs
        orientations: List[int]
            List of motif instance orientations

        Return
        ------
        instances: List[str]
            List of motif instances
        """
        instances = []
        for motif_idx, orientation in zip(motif_idx_list, orientations):
            instance_str = self.get_one_new_instance(
                motif_index=motif_idx)
            instances.append(self.orient_motif(
                current_instance=instance_str,
                orientation=orientation))
        return instances

    def orient_motif(
            self,
            current_instance: str,
            orientation: int) -> str:
        """ Reverse complementing an instance as necessary

        Parameters
        ----------
        current_instance: str
            String of a motif instance
        orientation: int
            0 or 1, where 0 means keeping the orientation and \
            1 means reverse complementing the motif instance.

        Return
        ------
        oriented_instance: str
            Sequence of an oriented instance
        """
        if orientation == 0:
            oriented_instance = sequtils.create_reverse_complement(
                    alphabet=self.motifs.alphabet_revcomp_pairs,
                    motif_instance=current_instance)
        else:
            oriented_instance = current_instance
        return oriented_instance
