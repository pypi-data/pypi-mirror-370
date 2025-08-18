"""Class to add motif instance(s) to sequences
author: Kata Ferenc
email: katalitf@uio.no
"""
from typing import List, Tuple
import numpy as np
from inmotifin.modules.data.motif import Motifs
from inmotifin.utils import sequtils


class Inserter:
    """Class to add motif instance(s) to sequences

    Class parameters
    ----------------
    to_replace: bool
        Whether the motif instance replaces background bases, \
        alternative is to insert by extending the bakground
    """

    def __init__(self, to_replace: bool) -> None:
        """Initialize inserter

        Parameters
        ----------
        to_replace: bool
            Value whether to replace background letters with motif instances. \
            If false: insert the instances and extend the sequence
        """
        self.to_replace = to_replace

    def set_to_replace(self, to_replace: bool) -> None:
        """Set whether to replace background letters with motif instances

        Parameters
        ----------
        to_replace: bool
            Value whether to replace background letters with motif instances. \
            If false: insert the instances and extend the sequence
        """
        self.to_replace = to_replace

    def add_single_instance(
            self,
            sequence: str,
            motif_instance: str,
            position: int) -> str:
        """Adds a given motif_instance in a background sequence by replacing \
        existing bases or by increasing the length

        Parameters
        ----------
        sequence: str
            String of the sequence used as background
        motif_instance: str
            motif instance to insert
        position: int
            the start location where the motif to be inserted within the
            background sequence

        Return
        ------
        new_sequence: str
            Sequence with instance inserted
        """
        str_seq = list(sequence)
        if self.to_replace:
            str_seq = str_seq[0:position] + \
                list(motif_instance) + \
                str_seq[position+len(motif_instance):]
        else:
            str_seq = str_seq[:position] + \
                list(motif_instance) + \
                str_seq[position:]
        new_sequence = ''.join(str_seq)
        return new_sequence

    def add_single_motif_probabilities(
            self,
            sequence: np.ndarray,
            motif: np.ndarray,
            position: int) -> np.ndarray:
        """Adds a given motif in a background probability array by replacing \
        existing bases or by increasing the length

        Parameters
        ----------
        sequence: np.ndarray
            Letter probabilities of the sequence used as background
        motif: np.ndarray
            PWM to insert
        position: int
            the start location where the motif to be inserted within the
            background sequence

        Return
        ------
        new_sequence: np.ndarray
            Letter probabilities of sequence with motif inserted
        """
        if self.to_replace:
            new_sequence = np.concatenate((
                sequence[:position],
                motif,
                sequence[position+motif.shape[0]:]))
        else:
            new_sequence = np.concatenate((
                sequence[:position],
                motif,
                sequence[position:]))
        return new_sequence

    def create_insert_positions(
            self,
            positions: List[Tuple[int]],
            motif_instances: List[str] = None,
            motif_ids: List[str] = None
            ) -> Tuple[List[Tuple[int]], List[str], List[str]]:
        """Reverse the positions to insert from the end \
            when bases are not replaced to avoid overwriting \
            the positions of the already inserted motifs. \
            Adjusts the motif list to match the lengths

        Parameters
        ----------
        positions: List[Tuple[int]]
            List of (start, end) position tuples.
        motif_instances: List[str]
            List of motif instance sequences
        motif_ids: List[str]
            List of motif IDs to insert

        Return
        ------
        positions: List[Tuple[int]]
            List of (start, end) position tuples in correct order.
        motif_instances: List[str]
            List of motif instance sequences in correct order
        motif_ids: List[str]
            List of motif IDs to insert in correct order
        """
        if not self.to_replace:
            positions.sort(reverse=True)
            if motif_instances is not None:
                motif_instances.sort(reverse=True)
            else:
                motif_ids.sort(reverse=True)
        return positions, motif_instances, motif_ids

    def generate_motif_in_sequence(
            self,
            sequence: str,
            motif_instances: List[str],
            positions: List[Tuple[int]]) -> str:
        """Function to insert all motif_instances into a background

        Parameters
        ----------
        sequence: str
            String of a background sequence to insert motif_instances to
        motif_instances: List[str]
            List of motif instance sequences
        positions: List[Tuple[int]]
            List of (start, end) position tuples.

        Return
        ------
        motif_in_sequence: str
            Sequence with motif instances inserted
        """
        insert_positions, motif_instances, _ = self.create_insert_positions(
            positions=positions,
            motif_instances=motif_instances)
        for idx, motif_inst in enumerate(motif_instances):
            sequence = self.add_single_instance(
                sequence=sequence,
                motif_instance=motif_inst,
                position=insert_positions[idx][0])
        return sequence

    def generate_probabilistic_motif_in_sequence(
            self,
            sequence: str,
            b_alphabet: str,
            b_alphabet_prior: np.ndarray,
            motifs: Motifs,
            motif_ids: List[str],
            orientation_list: List[int],
            positions: List[Tuple[int]]) -> np.ndarray:
        """Function to insert motifs into a probabilistic background sequence

        Parameters
        ----------
        sequence: str
            String of a background sequence to insert motif_instances to
        b_alphabet: str
            Background alphabet, default is "ACGT"
        b_alphabet_prior: np.ndarray
            Background alphabet prior probabilities
        motifs: Motifs
            Data class for motifs with names (key), PPM, alphabet and \
            alphabet pairs
        motif_ids: List[str]
            List of motif IDs to insert
        orientations: List[int]
            Mask for instances. List of 0s and 1s, where 0 means keeping the \
            orientation, 1 means reverse complementing the motif instance.
        positions: List[Tuple[int]]
            List of (start, end) position tuples.

        Return
        ------
        probabilistic_motif_in_sequence: np.ndarray
            Letter probabilities in sequence with motif instances inserted
        """
        if b_alphabet != motifs.alphabet:
            msg = "Background alphabet does not match motif alphabet. "
            msg += "Probabilistic motif-in-sequence array cannot be created."
            print(msg)
            return
        insert_positions, _, motif_ids = self.create_insert_positions(
            positions=positions,
            motif_ids=motif_ids)

        sequence_prob = np.tile(b_alphabet_prior, (len(sequence), 1))
        
        if len(motif_ids) == 0:
            return sequence_prob

        complementary_idx = sequtils.define_complementary_map_motif_array(
            alphabet=motifs.alphabet,
            alphabet_pairs=motifs.alphabet_revcomp_pairs)

        for idx, motif_id in enumerate(motif_ids):
            if orientation_list[idx] == 0:
                selected_motif = motifs.motifs[motif_id]
                oriented_motif = sequtils.create_reverse_complement_motif(
                    motif=selected_motif,
                    complementary_idx=complementary_idx)
            else:
                oriented_motif = motifs.motifs[motif_id]
            sequence_prob = self.add_single_motif_probabilities(
                sequence=sequence_prob,
                motif=oriented_motif,
                position=insert_positions[idx][0])
        return sequence_prob
