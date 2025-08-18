""" Sample from group and motif frequencies """
from typing import List
import numpy as np
from inmotifin.utils.baseutils import choice_from_dict
from inmotifin.modules.data.frequencies import Frequencies


class FrequencySampler:
    """ Class to select motif based on its background frequencies

    Class parameters
    ----------------
    frequencies: Frequencies
        Frequencies data class including probabilities of \
        groups and motifs within them
    num_groups_per_seq: int
        Number of groups to select in total
    rng: np.random.Generator
        Random generator for sampling
    """

    def __init__(
            self,
            frequencies: Frequencies,
            num_groups_per_seq: int,
            rng: np.random.Generator):
        """ Constructor

        Parameters
        ----------
        frequencies: Frequencies
            Frequencies data class including probabilities of \
            groups and motifs within them
        num_groups_per_seq: int
            Number of groups to select in total
        rng: np.random.Generator
            Random generator for sampling
        """
        self.frequencies = frequencies
        self.num_groups_per_seq = num_groups_per_seq
        self.rng = rng

    def select_groups(self) -> List[str]:
        """ Select groups based on their frequency and co-occurence \
            probability

        Return
        ------
        selected_ids: List[str]
            List of selected group ids
        """
        first_group = self.select_first_group()
        all_groups = sorted(self.select_rest_of_groups(
            num_groups_rest=self.num_groups_per_seq-1,
            base_group=first_group))
        all_groups_str = [str(top) for top in all_groups]
        all_groups_str.append(first_group)
        return all_groups_str

    def select_first_group(self) -> str:
        """ Start by selecting the first group given group frequencies

        Return
        ------
        selected_group: str
            ID of the selected group
        """
        selected_group = str(choice_from_dict(
            indict=self.frequencies.group_freq,
            size=1,
            rng=self.rng)[0])
        return selected_group

    def select_rest_of_groups(
            self,
            num_groups_rest: int,
            base_group: str) -> np.ndarray:
        """ Select a group given an already selected group

        Parameters
        ----------
        num_groups_rest: int
            Number of groups to select after the first one
        base_group: str
            ID of the already selected group

        Return
        ------
        selected_ids: np.ndarray
            Array of selected group ids
        """
        group_probs = self.frequencies.group_group_cooccurence_prob.loc[
            base_group,]

        selected_ids = choice_from_dict(
            indict=group_probs,
            size=num_groups_rest,
            rng=self.rng)

        return selected_ids

    def select_motifs_from_groups(
            self,
            group_ids: List[str],
            num_instances_per_seq: int) -> List[str]:
        """ Select motifs from given groups

        Parameters
        ----------
        group_ids: List[str]
            List of selected group ids
        num_instances_per_seq: int
            Number of motifs to select (per sequence)

        Return
        ------
        selected_motifs: List[str]
            List of selected motif IDs
        """
        num_motif_per_group = int(np.floor(
            num_instances_per_seq / self.num_groups_per_seq))
        all_selected_motifs = []
        for group in group_ids:
            prob_series = self.frequencies.motif_freq_per_group[group]
            selected_motifs = self.rng.choice(
                a=prob_series.index,
                size=num_motif_per_group,
                replace=True,
                p=prob_series.tolist())
            all_selected_motifs += list(selected_motifs)
        while len(all_selected_motifs) < num_instances_per_seq:
            # pick one more motif from one group
            one_more_group_idx = self.rng.choice(
                a=group_ids,
                size=1)[0]
            motif_probs = self.frequencies.motif_freq_per_group[
                one_more_group_idx]
            one_more_motif = self.rng.choice(
                a=motif_probs.index,
                size=1,
                p=motif_probs.tolist())
            all_selected_motifs.append(one_more_motif[0])
        return all_selected_motifs
