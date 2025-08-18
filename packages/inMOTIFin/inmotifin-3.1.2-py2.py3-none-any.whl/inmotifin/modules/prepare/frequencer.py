""" Class to generate motif and group background frequencies """
from typing import List, Dict
import numpy as np
import pandas as pd
from inmotifin.utils import mathutils
from inmotifin.utils.paramsdata.freqparams import FreqParams
from inmotifin.modules.data.frequencies import Frequencies
from inmotifin.modules.data.groups import Groups
from inmotifin.utils.fileops.reader import Reader
from inmotifin.utils.fileops.writer import Writer


class Frequencer:
    """Class to generate motif and group background frequencies, \
    that is the selection probability for each group and motif within

    Class parameters
    ----------------
    title: str
        Title of the analysis
    params: FreqParams
        Dataclass storing group_frequency_type, group_frequency_range, \
        motif_frequency_type, motif_frequency_range, group_freq_file and \
        motif_freq_file
    groups: groups
        The groups with ids and assigned motifs
    num_groups: int
        Number of groups
    reader: Reader
        File reader class to read in sequences if necessary
    writer: Writer
        instance of the writer class
    frequencies: Frequencies
        Data class for frequencies
    rng: np.random.Generator
        Random generator for random frequency sampling
    """

    def __init__(
            self,
            params: FreqParams,
            groups: Groups,
            reader: Reader,
            writer: Writer,
            rng: np.random.Generator) -> None:
        """ Constructor

        Parameters
        ----------
        params: FreqParams
            Dataclass storing group_frequency_type, group_frequency_range, \
            motif_frequency_type, motif_frequency_range, group_freq_file and \
            motif_freq_file
        groups: groups
            The groups with ids and assigned motifs
        reader: Reader
            File reader class to read in sequences if necessary
        writer: Writer
            instance of the writer class
        rng: np.random.Generator
            Random generator for random frequency sampling
        """
        self.title = writer.get_title()
        self.rng = rng
        self.params = params
        self.groups = groups
        self.reader = reader
        self.writer = writer
        self.num_groups = len(self.groups.groups)
        self.frequencies = None

    def get_frequencies(self) -> Frequencies:
        """ Getter for group and motif frequencies

        Return
        -------
        frequencies: Frequencies
            Data class for frequencies
        """
        return self.frequencies

    def assign_frequencies(self) -> None:
        """ Read in or simulate group and motif frequencies """
        if self.params.motif_freq_file is not None:
            motif_freq_per_group = self.read_motif_freq_per_group()
        else:
            motif_freq_per_group = self.assign_motif_frequencies()
            self.writer.pandas_to_tsv(
                dataframe=motif_freq_per_group,
                filename="motif_freq_per_group")
        if self.params.group_freq_file is not None:
            group_freq = self.read_group_freq()
        else:
            group_freq = self.assign_group_frequencies()
            self.writer.dict_to_tsv(
                data_dict=group_freq,
                filename="group_frequency")
        if self.params.group_group_file is not None:
            group_group_cooccurence_prob = self.read_group_group_cooc()
        else:
            group_group_cooccurence_prob = self.assign_group_group_cooc_probs()
            self.writer.pandas_to_tsv(
                dataframe=group_group_cooccurence_prob,
                filename="group_group_cooccurence_probabilities")

        self.frequencies = Frequencies(
            group_freq=group_freq,
            motif_freq_per_group=motif_freq_per_group,
            group_group_cooccurence_prob=group_group_cooccurence_prob)

    def read_motif_freq_per_group(self) -> pd.DataFrame:
        """ Read in motif frequencies

        Return
        ------
        motif_freq: pd.DataFrame
            Motif frequencies per group from file
        """
        return self.reader.read_tsv_to_pandas(
            pandas_dftsv_path=self.params.motif_freq_file)

    def read_group_freq(self) -> Dict[str, float]:
        """ Read in group frequencies

        Return
        ------
        group_freq: Dict[str, float]
            Dictionary of group IDs and their expected occurrence \
            frequencies
        """
        group_freq_raw = self.reader.read_twocolumn_tsv(
            twocolumns_tsv_path=self.params.group_freq_file)
        group_freq = {}
        for group_id, group_p in group_freq_raw.items():
            group_freq[group_id] = float(group_p[0])
        return group_freq

    def read_group_group_cooc(self) -> pd.DataFrame:
        """ Read in group group cooccurences

        Return
        ------
        group_group: pd.DataFrame
            Pandas dataframe of co-occurrences of group pairs
        """
        return self.reader.read_tsv_to_pandas(
            pandas_dftsv_path=self.params.group_group_file)

    def assign_group_frequencies(self) -> Dict[str, float]:
        """ Simulate group frequencies

        Return
        ------
        group_freq: Dict[str, float]
            Dictionary of group IDs and their expected occurrence \
            frequencies
        """
        group_freq = self.simulate_background_freq(
            freq_type=self.params.group_frequency_type,
            freq_range=self.params.group_frequency_range,
            ids=sorted(self.groups.groups.keys()))
        return group_freq

    def assign_motif_frequencies(self) -> pd.DataFrame:
        """ Simulate motif frequencies within groups

        Return
        ------
        motif_group_df: pd.DataFrame
            Pandas dataframe of motif frequencies per group
        """
        motif_freq_per_group = {}
        for group_key, group_value in self.groups.groups.items():
            motif_freq_per_group[group_key] = \
                self.simulate_background_freq(
                    freq_type=self.params.motif_frequency_type,
                    freq_range=self.params.motif_frequency_range,
                    ids=group_value)
        motif_group_df = pd.DataFrame.from_dict(
            motif_freq_per_group,
            orient="columns")
        motif_group_df.fillna(value=0, inplace=True)
        return motif_group_df

    def assign_group_group_cooc_probs(self) -> pd.DataFrame:
        """ Simulate the probability of selecting groupX given \
            previously selected groupY

        Return
        ------
        group_group_cooccurence_prob: pd.DataFrame
            Pandas dataframe of co-occurrences of group pairs
        """
        group_ids = sorted(self.groups.groups.keys())
        remaining_prob = 1 - self.params.concentration_factor
        if self.params.group_group_type.lower() == "random":
            group_group_matrix = self.pairs_random(
                remaining_prob=remaining_prob)
        elif self.params.group_group_type.lower() == "uniform":
            group_group_matrix = self.symmetric_pairs_uniform(
                remaining_prob=remaining_prob)
        else:
            raise ValueError("only random and uniform types are supported")
        group_group_cooccurence_prob = pd.DataFrame(
            group_group_matrix,
            columns=group_ids,
            index=group_ids)
        return group_group_cooccurence_prob

    def symmetric_pairs_uniform(
            self,
            remaining_prob: float) -> np.ndarray:
        """ Creating a matrix of group-group and their co-occurence \
            probability: off-diagonals are uniform

        Parameters
        ----------
        remaining_prob: float
            The probability remaining after assigning self co-occurence

        Return
        ------
        group_prob_arr: np.ndarray
            Array containing probabilities for group co-occurence
        """
        if self.num_groups == 1:
            off_diag_prob = 0
        else:
            off_diag_prob = remaining_prob/(self.num_groups-1)
        group_prob_arr = np.zeros(
            (self.num_groups, self.num_groups),
            dtype=float)
        np.fill_diagonal(group_prob_arr, self.params.concentration_factor)
        group_prob_arr[np.triu_indices(self.num_groups, k=1)] = off_diag_prob
        group_prob_arr[np.tril_indices(self.num_groups, k=-1)] = off_diag_prob
        return group_prob_arr

    def pairs_random(
            self,
            remaining_prob: float) -> np.ndarray:
        """ Creating a matrix of group-group and their co-occurence \
            probability: off-diagonals are random but rows sum to 1

        Parameters
        ----------
        remaining_prob: float
            The probability remaining after assigning self co-occurence

        Return
        ------
        group_prob_arr: np.ndarray
            Array containing probabilities for group co-occurence
        """
        nt = self.num_groups
        group_prob_arr = np.zeros((nt, nt), dtype=float)
        # fill in the rest of the matrix with random values
        # in a symmetric fashion and all rows sum to 1
        for rowidx in range(0, nt):
            rest_of_prob = remaining_prob
            for colidx in range(0, nt):
                if rowidx == colidx:
                    # fill diagonal with fix values
                    group_prob_arr[rowidx, colidx] = \
                        self.params.concentration_factor
                elif colidx == nt-1:
                    # ensure that rows sum to 1
                    group_prob_arr[rowidx, colidx] = rest_of_prob
                elif (rowidx == nt-1) and (colidx == nt-2):
                    # ensure that rows sum to 1
                    group_prob_arr[rowidx, colidx] = rest_of_prob
                else:
                    # otherwise, sample random value below sum(1)
                    group_prob_arr[rowidx, colidx] = self.rng.uniform(
                        low=0.0,
                        high=rest_of_prob)
                    rest_of_prob -= group_prob_arr[rowidx, colidx]
        return group_prob_arr

    def simulate_background_freq(
            self,
            freq_type: str,
            freq_range: int,
            ids: List[str]) -> Dict[str, float]:
        """ Simulate background frequencies

        Parameters
        ----------
        freq_type: str
            Way to generate frequencies. Currently random and uniform are \
            supported. Random refers to random sampling from a range of \
            probabilities given freq_range. Uniform refers to assigning \
            equal probabilities to all items.
        freq_range: int
            The expected max difference between an unlikely and a likely event\
            . E.g. if set to 100, a low probability event can be 100x less \
            likely than a high probability one
        ids: List[str]
            The IDs of the items to assign frequency to

        Return
        ------
        background_freq: Dict[str, float]
            Probability assigned to each element of the given ids
        """
        if freq_type.lower() == "random":
            background_freq = self.simulate_background_freq_random(
                difference_width=freq_range,
                ids=ids)
        elif freq_type.lower() == "uniform":
            background_freq = self.simulate_background_freq_uniform(
                ids=ids)
        else:
            raise ValueError("only random and uniform types are supported")
        return background_freq

    def simulate_background_freq_random(
            self,
            difference_width: int,
            ids: List[str]) -> Dict[str, float]:
        """ Simulate background frequencies random uniform

        Parameters
        ----------
        difference_width: int
            The expected max difference between an unlikely and a likely event\
            . E.g. if set to 100, a low probability event can be 100x less \
            likely than a high probability one
        ids: List[str]
            The IDs of the items to assign frequency to

        Return
        ------
        background_freq: Dict[str, float]
            Probability assigned to each element of the given ids
        """
        background_freq = self.rng.integers(
            # ensure that the lowest value is 1, so that no motif gets zero
            low=1,
            high=difference_width,
            size=len(ids))
        norm_background_freq = mathutils.normalize_array(
            my_array=background_freq)
        background_freq = dict(zip(ids, norm_background_freq))
        return background_freq

    def simulate_background_freq_uniform(
            self,
            ids: List[str]) -> Dict[str, float]:
        """ Simulate equal background frequencies for all items

        Parameters
        ----------
        ids: List[str]
            The IDs of the items to assign frequency to

        Return
        ------
        background_freq: Dict[str, float]
            Probability assigned to each element of the given ids
        """
        uniform_background_freq = [1/len(ids) for _ in range(len(ids))]
        background_freq = dict(zip(ids, uniform_background_freq))
        return background_freq
