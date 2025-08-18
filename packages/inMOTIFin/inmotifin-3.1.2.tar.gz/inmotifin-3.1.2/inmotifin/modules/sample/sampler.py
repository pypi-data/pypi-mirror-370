""" Main class of sampling
author: Kata Ferenc
email: katalitf@uio.no
"""
from typing import List, Dict, Any, Tuple
import numpy as np
from inmotifin.utils.fileops.reader import Reader
from inmotifin.utils.paramsdata.samplingparams import SamplingParams
from inmotifin.utils.paramsdata.positionparams import PositionParams
from inmotifin.modules.sample.backgroundsampler import BackgroundSampler
from inmotifin.modules.sample.motifinstancer import MotifInstancer
from inmotifin.modules.sample.frequencysampler import FrequencySampler
from inmotifin.modules.sample.positioner import Positioner
from inmotifin.modules.sample.inserter import Inserter


class Sampler:
    """ Controller class for sampling

    Class parameters
    ----------------
    sampling_params: SamplingParams
        Data class with sampling parameters
    position_params: PositionParams
        Data class with positioning parameters
    reader: Reader
        File reader class to read in sequences if necessary
    rng: np.random.Generator
        Random generator for sampling
    motifs: Motifs
        Data class for motifs with names (key) and PPM
    instancer: MotifInstancer
        Class for sampling instances from motifs
    frequencer: FrequencySampler
        Class for sampling groups and motifs based on their frequencies
    backgrounder: BackgroundSampler
        Class for sampling from the pool of the backgrounds
    inserter: Inserter
        Class for inserting instances into backgrounds given \
        the sampled positions
    """

    def __init__(
            self,
            sampling_params: SamplingParams,
            position_params: PositionParams,
            data_for_simulation: Dict[str, Any],
            reader: Reader,
            rng: np.random.Generator):
        """ Constructor

        Parameters
        ----------
        sampling_params: SamplingParams
            Data class with sampling parameters
        position_params: PositionParams
            Data class with positioning parameters
        data_for_simulation: Dict[str, Any]
            Initialized motifs, backgrounds, groups, and frequencies
        reader: Reader
            File reader class to read in sequences if necessary
        rng: np.random.Generator
            Random generator for sampling
        """
        self.sampling_params = sampling_params
        self.position_params = position_params
        self.reader = reader
        self.rng = rng
        self.motifs = data_for_simulation["motifs"]
        self.instancer = MotifInstancer(
            motifs=self.motifs,
            rng=self.rng)
        self.frequencer = FrequencySampler(
            frequencies=data_for_simulation["frequencies"],
            num_groups_per_seq=self.sampling_params.num_groups_per_sequence,
            rng=self.rng)
        self.backgrounder = BackgroundSampler(
            backgrounds=data_for_simulation["backgrounds"],
            rng=self.rng)
        self.inserter = Inserter(
            to_replace=position_params.to_replace)

    def get_num_instances(self) -> int:
        """ Return the number of instances per sequence either by
        sampling from Poisson or a fixed number

        Return
        ------
        _: int
            Number of instances per sequence
        """
        if self.sampling_params.n_instances_per_sequence is None:
            ps_lambda = self.sampling_params.lambda_n_instances_per_sequence
            return self.rng.poisson(lam=ps_lambda)
        if self.sampling_params.n_instances_per_sequence > 0:
            return self.sampling_params.n_instances_per_sequence
        raise ValueError("either n_instances_per_sequence or \
            lambda_n_instances_per_sequence should be set to not None")

    def select_groups(self) -> List[str]:
        """ Select groups

        Return
        ------
        _: List[str]
            List of group IDs
        """
        return self.frequencer.select_groups()

    def select_motifs(
            self,
            group_ids: List[str],
            num_instances_per_seq: int) -> List[str]:
        """ Select motifs from given groups
        Parameters
        ----------
        group_ids: List[str]
            ID of the selected groups
        num_instances_per_seq: int
            Number of instances to be selected per sequence

        Return
        ------
        _: List[str]
            List of selected motif IDs
        """
        return self.frequencer.select_motifs_from_groups(
            group_ids=group_ids,
            num_instances_per_seq=num_instances_per_seq)

    def select_orientations(
            self,
            num_instances_per_seq: int) -> List[int]:
        """ Sample orientation for each instance
        Parameters
        ----------
        num_instances_per_seq: int
            Number of instances to be selected per sequence

        Return
        ------
        _: List[int]
            List of 0 or 1, where 0 means original motif instance,\
            1 means reverse complemented
        """
        orientations = self.rng.binomial(
            n=1,
            p=self.sampling_params.orientation_probability,
            size=num_instances_per_seq)
        orientation_nums = [int(ori) for ori in orientations]
        return orientation_nums

    def sample_instances(
            self,
            motif_idx_list: List[str],
            orientations: List[int]) -> List[str]:
        """ Access generated instances from motifs
        Parameters
        ----------
        motif_idx_list: List[str]
            List of motif IDs
        orientations: List[int]
            Mask for instances. List of 0s and 1s, where 0 means keeping the \
            orientation, 1 means reverse complementing the motif instance.

        Return
        ------
        oriented_instances: List[str]
            List of instances in the correct orientation
        """
        oriented_instances = self.instancer.sample_instances(
            motif_idx_list=motif_idx_list,
            orientations=orientations)
        return oriented_instances

    def get_background_id(self) -> str:
        """ Access a single background sequence ID

        Return
        ------
        _: str
            An ID for a selected background sequence
        """
        return self.backgrounder.get_background_id()

    def get_backgrounds(self, num_backgrounds: int) -> List[str]:
        """ Access a list of background sequences
        Parameters
        ----------
        num_backgrounds: int
            Number of requested backgrounds
        """
        return self.backgrounder.get_backgrounds(
            num_backgrounds=num_backgrounds)

    def get_positions(
            self,
            background_id: str,
            instances: List[str]) -> List[Tuple[int]]:
        """ Accessing sequence-specific positions
        Parameters
        ----------
        background_id: str
            ID of the selected background
        instances: List[str]
            List of motif instances

        Return
        ------
        selected_positions: List[Tuple[int]]
            Selected positions list of (start, end)
        """
        background_seq = self.backgrounder.get_single_background(
            selected_id=background_id)
        if len(instances) == 0:
            return [(0,0)]
        positioner = Positioner(
            params=self.position_params,
            selected_instances=instances,
            seq_length=len(background_seq),
            reader=self.reader,
            rng=self.rng)
        selected_positions = positioner.select_positions()
        self.inserter.set_to_replace(
            to_replace=positioner.get_to_replace())
        return selected_positions.positions

    def get_motif_in_sequence(
            self,
            background_id: str,
            oriented_instances: List[str],
            positions: List[Tuple[int]]) -> str:
        """ Providing access to sequences with inserted instances
        Parameters
        ----------
        background_id: str
            ID of the selected background
        oriented_instances: List[str]
            List of the selected instances in correct orientation
        positions: List[Tuple[int]]
            List of (start, end) position tuples.

        Return
        ------
        _: str
            Final sequence with motifs inserted
        """
        background_seq = self.backgrounder.get_single_background(
            selected_id=background_id)
        if len(oriented_instances) == 0:
            return background_seq
        return self.inserter.generate_motif_in_sequence(
            sequence=background_seq,
            motif_instances=oriented_instances,
            positions=positions)

    def get_prob_motif_in_sequence(
            self,
            background_id: str,
            motif_idx_list: List[str],
            orientations: List[int],
            positions: List[Tuple[int]]) -> np.ndarray:
        """ Providing access to sequences with inserted instances
        Parameters
        ----------
        background_id: str
            ID of the selected background
        motif_idx_list: List[str]
            List of motif IDs
        orientations: List[int]
            Mask for instances. List of 0s and 1s, where 0 means keeping the \
            orientation, 1 means reverse complementing the motif instance.
        positions: List[Tuple[int]]
            List of (start, end) position tuples.

        Return
        ------
        _: np.ndarray
            Letter probabilities of final sequence with motifs inserted
        """
        background_seq = self.backgrounder.get_single_background(
            selected_id=background_id)
        return self.inserter.generate_probabilistic_motif_in_sequence(
            sequence=background_seq,
            b_alphabet=self.backgrounder.get_b_alphabet(),
            b_alphabet_prior=self.backgrounder.get_b_alphabet_prior(),
            motifs=self.motifs,
            motif_ids=motif_idx_list,
            orientation_list=orientations,
            positions=positions)
