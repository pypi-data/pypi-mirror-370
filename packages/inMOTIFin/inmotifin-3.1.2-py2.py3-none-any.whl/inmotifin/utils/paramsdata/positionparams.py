""" Data storage for positioning parameters """
from typing import List
from dataclasses import dataclass


@dataclass
class PositionParams:
    """ Class for keeping track of parameters for positioning

    Class parameters
    ----------------
    position_type: str
        Type of position distribution, possible values: \
        "central", "left_central", "right_central", "uniform", \
        "gaussian". default is "central"
    position_means: List[int]
        List of means for the position distribution, used \
        when position_type is "gaussian"
    position_variances: List[float]
        List of variances for the position distribution, used \
        when position_type is "gaussian"
    to_replace: bool
        Whether to replace the positions when generating \
        new positions. False when position_type is "gaussian".
    """
    position_type: str
    position_means: List[int]
    position_variances: List[float]
    to_replace: bool

    def __post_init__(self):
        """ Set default values for parameters if not provided """
        if self.position_type is None:
            self.position_type = "central"
