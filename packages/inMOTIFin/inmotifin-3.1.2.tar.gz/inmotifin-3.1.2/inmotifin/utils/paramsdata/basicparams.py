""" Data storage for basic parameters """
from dataclasses import dataclass


@dataclass
class BasicParams:
    """ Class for keeping track of basic parameters

    Class parameters
    ----------------
    title: str
        Title of the analysis
    workdir: str
        Working directory for the analysis, default is current directory. \
        Note: it should be a relative path. Absolute paths are not supported.
    seed: int
        Random seed for reproducibility, default is None
    """
    title: str
    workdir: str
    seed: int

    def __post_init__(self):
        """ Set default values for parameters if not provided """
        if self.workdir is None:
            self.workdir = '.'
