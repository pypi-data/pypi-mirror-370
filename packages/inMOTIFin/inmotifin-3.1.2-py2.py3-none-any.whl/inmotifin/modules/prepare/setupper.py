""" Organizes the setup of the simulation by creating
motifs, groups, frequencies and backgrounds """
import numpy as np

from inmotifin.utils.paramsdata.motifparams import MotifParams
from inmotifin.utils.paramsdata.backgroundparams import BackgroundParams
from inmotifin.utils.paramsdata.groupparams import GroupParams
from inmotifin.utils.paramsdata.freqparams import FreqParams

from inmotifin.modules.prepare.motifer import Motifer
from inmotifin.modules.prepare.backgrounder import Backgrounder
from inmotifin.modules.prepare.grouper import Grouper
from inmotifin.modules.prepare.frequencer import Frequencer

from inmotifin.modules.data.motif import Motifs
from inmotifin.modules.data.background import Backgrounds
from inmotifin.modules.data.groups import Groups
from inmotifin.modules.data.frequencies import Frequencies

from inmotifin.utils.fileops.reader import Reader
from inmotifin.utils.fileops.writer import Writer


class Setupper:
    """ Class to organize setup
    Class parameters
    ----------------
    motif_alphabet: str
        The allowed characters in the motif (eg [A, C, G, T] or 'ACGT')
    """

    def __init__(
            self,
            reader: Reader,
            writer: Writer,
            motif_params: MotifParams,
            background_params: BackgroundParams,
            group_params: GroupParams,
            frequency_params: FreqParams,
            rng: np.random.Generator) -> None:
        """ Constructor
        Parameters
        ----------
        reader: Reader
            instance of the reader class
        writer: Writer
            instance of the writer class
        motif_params: MotifParams
            Parameters related to motif creation or reading
        background_params: BackgroundParams
            Parameters related to background creation or reading
        group_params: groupParams
            Parameters related to group creation or reading
        frequency_params: FreqParams
            Parameters related to group and motif frequency creation or reading
        rng: np.random.Generator
            Random generator for sampling
        """
        self.group_params = group_params
        self.frequency_params = frequency_params
        self.reader = reader
        self.writer = writer
        self.rng = rng
        self.motifer = Motifer(
            params=motif_params,
            rng=self.rng,
            reader=self.reader,
            writer=self.writer)
        self.backgrounder = Backgrounder(
            params=background_params,
            reader=self.reader,
            writer=self.writer,
            rng=self.rng)
        # initialized after motifs are created
        self.grouper = None
        # initialized after groups are created
        self.frequencer = None

    def create_motifs(self) -> Motifs:
        """ Create and save or read in motifs """
        self.motifer.create_motifs()
        motifs = self.motifer.get_motifs()
        print("Motifs created / read in")
        self.grouper = Grouper(
            params=self.group_params,
            motif_ids=motifs.motif_ids,
            reader=self.reader,
            writer=self.writer,
            rng=self.rng)
        return motifs

    def create_backgrounds(self) -> Backgrounds:
        """ Create and save or read in backgrounds """
        self.backgrounder.create_backgrounds()
        backgrounds = self.backgrounder.get_backgrounds()
        print("Backgrounds created / read in")
        return backgrounds

    def create_groups(self) -> Groups:
        """ Create and save or read in groups """
        self.grouper.create_groups()
        groups = self.grouper.get_groups()
        self.frequencer = Frequencer(
            params=self.frequency_params,
            groups=groups,
            reader=self.reader,
            writer=self.writer,
            rng=self.rng)
        print("Groups created / read in")
        return groups

    def create_frequencies(self) -> Frequencies:
        """ Create background frequencies of groups and save to tsv """
        self.frequencer.assign_frequencies()
        print("Frequencies created / read in")
        return self.frequencer.get_frequencies()
