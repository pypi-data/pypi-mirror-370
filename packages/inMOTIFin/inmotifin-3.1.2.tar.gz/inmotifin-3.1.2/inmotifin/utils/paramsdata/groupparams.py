""" Data storage for group parameters """
from typing import List
from dataclasses import dataclass
import math


@dataclass
class GroupParams:
    """ Class for keeping track of parameters for groups

    Class parameters
    ----------------
    number_of_groups: int
        Number of groups to generate, default is 1
    max_group_size: int
        Maximum size of each group, default is infinity
    group_size_binom_p: float
        Probability of success in the binomial distribution for \
        group size, default is 1
    group_motif_assignment_file: List[str]
        List of group motif assignment files, default is empty
    """
    number_of_groups: int
    max_group_size: int
    group_size_binom_p: float
    group_motif_assignment_file: List[str]

    def __post_init__(self):
        """ Set default values for parameters if not provided """
        if self.number_of_groups is None:
            self.number_of_groups = 1
        if self.max_group_size is None:
            self.max_group_size = math.inf
        if self.group_size_binom_p is None:
            self.group_size_binom_p = 1
