""" Data storage for dimer parameters """
from typing import List
from dataclasses import dataclass


@dataclass
class DimerParams:
    """ Class for keeping track of parameters for dimers

    Class parameters
    ----------------
    motif_files: List[str]
        List of motif file(s) to use for dimerisation
    jaspar_db_version: str
        Version of the JASPAR database to use when Jaspar \
        IDs are provided in the motif file(s)
    dimerisation_rule_path: str
        Path to the dimerisation rules file
    """
    motif_files: List[str]
    jaspar_db_version: str
    dimerisation_rule_path: str
