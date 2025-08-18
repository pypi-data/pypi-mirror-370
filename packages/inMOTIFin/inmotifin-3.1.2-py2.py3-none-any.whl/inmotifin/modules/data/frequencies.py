""" Data class for frequencies """
from typing import Dict
from dataclasses import dataclass, field
import pandas as pd


@dataclass
class Frequencies:
    """ Class for keeping track of frequencies

    Class parameters
    ----------------
    num_groups: int
        Number of groups
    group_freq: Dict[str, float]
        Dictionary of group IDs and their expected occurrence frequencies
    motif_freq_per_group: pd.DataFrame
        Dataframe of expected frequencies of motifs per group
    group_group_cooccurence_prob: pd.DataFrame
        Dataframe of expected co-occurrence probability of group pairs
    """
    num_groups: int = field(init=False)
    group_freq: Dict[str, float]
    motif_freq_per_group: pd.DataFrame
    group_group_cooccurence_prob: pd.DataFrame

    def __post_init__(self):
        """ Calculate and store number of groups """
        self.num_groups = len(self.group_freq.keys())
