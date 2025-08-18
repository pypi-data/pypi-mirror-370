""" Data class for groups """
from typing import Dict, List
from dataclasses import dataclass


@dataclass
class Groups:
    """ Class for keeping track of groups

    Class parameters
    ----------------
    groups: Dict[str, List[str]]
        Dictionary of group IDs and the motifs within each group
    """
    groups: Dict[str, List[str]]
