""" Data class for positions """
from typing import Tuple, List
from dataclasses import dataclass


@dataclass
class Positions:
    """ Class for keeping track of positions

    Class parameters
    ----------------
    positions: List[Tuple[int]]
        List of start and end of positions
    to_replace: bool
        Whether to replace background bases or insert in between existing bases
    """
    positions: List[Tuple[int]]
    to_replace: bool
