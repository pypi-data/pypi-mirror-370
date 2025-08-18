""" Data storage for group and motif frequency parameters """
from dataclasses import dataclass


@dataclass
class FreqParams:
    """ Class for keeping track of parameters for group and motif frequencies

    Class parameters
    ----------------
    group_frequency_type: str
        Type of group frequency distribution ("uniform", "random")
    group_frequency_range: int
        The range of the potential differences between a frequent \
        and a rare group
    motif_frequency_type: str
        Type of motif frequency distribution ("uniform", "random")
    motif_frequency_range: int
        The range of the potential differences between a frequent \
        and a rare motif
    group_group_type: str
        Type of group-group interaction distribution on the off-diagonal \
        ("uniform", "random")
    concentration_factor: float
        The preference of each groups to be selected again when \
        selecting more than one group for insertion. Value between 0 and 1.
    group_freq_file: str
        File name for group frequency data
    motif_freq_file: str
        File name for motif frequency data
    group_group_file: str
        File name for group-group interaction data
    """
    group_frequency_type: str
    group_frequency_range: int
    motif_frequency_type: str
    motif_frequency_range: int
    group_group_type: str
    concentration_factor: float
    group_freq_file: str
    motif_freq_file: str
    group_group_file: str

    def __post_init__(self):
        """ Set default values for parameters if not provided """
        if self.group_frequency_type is None:
            self.group_frequency_type = "uniform"
        if self.motif_frequency_type is None:
            self.motif_frequency_type = "uniform"
        if self.group_group_type is None:
            self.group_group_type = "uniform"
        if self.concentration_factor is None:
            self.concentration_factor = 1
