"""Class to select positions where motif instances are to be inserted
author: Kata Ferenc
email: katalitf@uio.no
"""

from typing import List, Tuple
import numpy as np
from inmotifin.utils.paramsdata.positionparams import PositionParams
from inmotifin.modules.data.positions import Positions
from inmotifin.utils.fileops.reader import Reader


class Positioner:
    """ Class to select positions where motif instances are to be inserted

    Class parameters
    ----------------
    params: PositionParams
        Dataclass storing position_type, position_means, \
        position_variances, and to_replace (insertion type)
    motif_lengths: List[int]
        List of the length of the motif instances to be inserted
    seq_length: int
        Length of the background sequence
    positions: Positions
        Start and end indeces where the motif instance should be inserted
    reader: Reader
        Fileops class with reading functionalities
    rng: np.random.Generator
        Random generator for length (uniform from integeres)
    """

    def __init__(
            self,
            params: PositionParams,
            selected_instances: List[str],
            seq_length: int,
            reader: Reader,
            rng: np.random.Generator) -> None:
        """ Initialize positioner

        Parameters
        ----------
        params: PositionParams
            Dataclass storing position_type, position_means, \
            position_variances, and to_replace (insertion type)
        selected_instances: List[str]
            List of motif instances to be inserted
        seq_length: int
            Length of the background sequence
        reader: Reader
            Fileops class with reading functionalities
        rng: np.random.Generator
            Random generator for length (uniform from integeres)
        """
        self.params = params
        self.motif_lengths = [len(inst) for inst in selected_instances]
        self.seq_length = seq_length
        self.reader = reader
        self.rng = rng
        self.positions = None

    def get_positions(self) -> Positions:
        """ Getter for positions class

        Return
        ------
        positions: Positions
            Dataclass of the start and end values of the selected positions
        """
        return self.positions

    def set_positions(self, positions: Positions) -> None:
        """ Setter for positions class

        Parameters
        ----------
        positions: Positions
            Class with start and end indeces where the motif instance \
            should be inserted
        """
        self.positions = positions

    def get_to_replace(self) -> bool:
        """ Getter for to_replace parameter

        Return
        ------
        _: bool
            True if the motif instances should replace background bases
        """
        return self.params.to_replace

    def check_overlap(
            self,
            current_positions: List[Tuple[int]],
            start_idx: int,
            end_idx: int) -> bool:
        """ Helper function to assess overlapping motifs

        Parameters
        ----------
        current_positions: List[Tuple[int]]
            Current list of positions
        start_idx: int
            Start index of the motif
        end_idx:int
            End index of the motif

        Return
        ------
        _: bool
            True if there is overlap
        """
        # check if the positions would be overlapping
        candidate_pos = set(range(start_idx, end_idx+1))
        for pos in current_positions:
            existing_pos = set(range(pos[0], pos[1]+1))
            if len(existing_pos.intersection(candidate_pos)) > 0:
                return True
        return False

    def check_lengths(self) -> None:
        """ Helper function to check if motif instances would fit into \
            background sequence used when the motifs are replacing \
            background bases
        """
        # check if any motif is longer than the background
        total_motif_len = sum(self.motif_lengths)
        longest_motif = max(self.motif_lengths)
        num_motifs = len(self.motif_lengths)
        left_side = num_motifs * (longest_motif-1)
        right_side = self.seq_length - total_motif_len + longest_motif
        if left_side >= right_side:
            raise AssertionError(
                f"Not enough bases to safely insert motif instance \
                Sequence length is {self.seq_length}, \
                motif lengths are {self.motif_lengths}. \
                Choose a longer background or shorter motif(s)")

    def check_central_positions(
            self,
            central_position: List[Tuple[int]]) -> None:
        """ Assert that the start and end positions are within bounds

        Parameters
        ----------
        central_position: List[Tuple[int]]
            List of positions that should be within the bounds of \
            the length of the background
        """
        is_ok = True
        if 0 > central_position[0][0]:
            is_ok = False
        if central_position[0][1] > self.seq_length:
            is_ok = False

        if not is_ok:
            message = "Too short background compared to motif length"
            raise AssertionError(message)

    def select_single_position_replacer(
            self,
            l_motif: int) -> Tuple[int]:
        """ Select a single position within background ranges including motif

        Parameters
        ----------
        l_motif: int
            Length of the motif to be inserted

        Return
        ------
        start: int
            Start coordinate
        end: int
            End coordinate
        """
        start = int(self.rng.integers(0, self.seq_length - l_motif + 1))
        end = start + l_motif - 1
        return start, end

    def select_positions_replace(self) -> None:
        """Generate positions within bacgkround sequence to insert motif \
            instances, ensure that motif instances are not overlapping \
            each other, motif instances replacing background bases.
        """
        positions = []
        self.check_lengths()
        for l_motif in self.motif_lengths:
            start, end = self.select_single_position_replacer(l_motif=l_motif)
            while self.check_overlap(positions, start, end):
                start, end = self.select_single_position_replacer(
                    l_motif=l_motif)
            positions.append((start, end))
        self.positions = Positions(
            positions=positions,
            to_replace=self.params.to_replace)

    def select_positions_inserted(self) -> None:
        """ Generate positions within background sequence to insert motif \
            instances, insert motif instances without replacing \
            background bases. Note: both positions are the start as \
            insertion is non replacing
        """
        positions = []
        num_motifs = len(self.motif_lengths)
        for _ in range(num_motifs):
            start = int(self.rng.integers(0, self.seq_length))
            positions.append((start, start))
        self.positions = Positions(
            positions=positions,
            to_replace=self.params.to_replace)

    def select_central_position(self) -> None:
        """ Calculate central position at the middle of the motif """
        if len(self.motif_lengths) > 1:
            raise ValueError(
                "Cannot align more than one motif to the center. \
                Use uniform or gaussian instead.")
        half_seq = int(self.seq_length / 2)
        half_motif = int(self.motif_lengths[0] / 2)
        if self.motif_lengths[0] % 2 == 1:
            central_position = [(half_seq - half_motif, half_seq + half_motif)]
        else:
            central_position = [
                (half_seq - half_motif, half_seq + half_motif - 1)]
        self.check_central_positions(central_position=central_position)
        self.positions = Positions(
            positions=central_position,
            to_replace=self.params.to_replace)

    def select_leftcentral_position(self) -> None:
        """ Calculate central position at the left side of the motif """
        if len(self.motif_lengths) > 1:
            raise ValueError(
                "Cannot align more than one motif to the center. \
                Use uniform or gaussian instead.")
        half_seq = int(self.seq_length / 2)
        central_position = [(half_seq, half_seq + self.motif_lengths[0] - 1)]
        self.check_central_positions(central_position=central_position)
        self.positions = Positions(
            positions=central_position,
            to_replace=self.params.to_replace)

    def select_rightcentral_position(self) -> None:
        """ Calculate central position at the right side of the motif """
        if len(self.motif_lengths) > 1:
            raise ValueError(
                "Cannot align more than one motif to the center. \
                Use uniform or gaussian instead.")
        half_seq = int(self.seq_length / 2)
        central_position = [(half_seq - self.motif_lengths[0], half_seq - 1)]
        self.check_central_positions(central_position=central_position)
        self.positions = Positions(
            positions=central_position,
            to_replace=self.params.to_replace)

    def select_gaussian_inserted(self) -> None:
        """ Sample positions following Gaussian distribution \
            centered around k positions. Only for inserting motif \
            without replacing background bases."""
        means = self.params.position_means
        variances = self.params.position_variances
        num_motifs = len(self.motif_lengths)
        k_per_center = num_motifs / len(means)
        positions = []
        center_count = 0
        for k in range(num_motifs):
            if k > (k_per_center * (center_count + 1)):
                center_count += 1
            start = int(self.rng.normal(
                means[center_count],
                variances[center_count]))
            # limiting so that it is within the boundaries of the sequence
            start = min(max(start, 0), self.seq_length)
            positions.append((start, start))
        self.params.to_replace = False
        self.positions = Positions(
            positions=positions,
            to_replace=self.params.to_replace)

    def select_positions(self) -> Positions:
        """ Main function to position selector

        Return
        ------
        positions: Positions
            Dataclass of selected start and end positions
        """
        if self.params.position_type.lower() == "uniform":
            if self.params.to_replace:
                self.select_positions_replace()
            else:
                self.select_positions_inserted()
        elif self.params.position_type.lower() == "central":
            self.select_central_position()
        elif self.params.position_type.lower() == "left_central":
            self.select_leftcentral_position()
        elif self.params.position_type.lower() == "right_central":
            self.select_rightcentral_position()
        elif self.params.position_type.lower() == "gaussian":
            self.select_gaussian_inserted()
        else:
            raise ValueError(
                f"position_type parameter is \
                {self.params.position_type}, which is not an \
                accepted input. Please select one of: \
                uniform, central, left_central, right_central, gaussian")

        return self.positions
