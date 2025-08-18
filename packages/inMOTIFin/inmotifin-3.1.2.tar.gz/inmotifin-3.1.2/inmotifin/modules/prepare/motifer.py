"""Class to generate and select sequence motifs
author: Kata Ferenc
email: katalitf@uio.no
"""
from typing import List, Dict
import numpy as np
from inmotifin.utils.paramsdata.motifparams import MotifParams
from inmotifin.modules.data.motif import Motifs
from inmotifin.utils.fileops.reader import Reader
from inmotifin.utils.fileops.writer import Writer


class Motifer:
    """Class to generate and select sequence motifs

    Class parameters
    ----------------
    title: str
        Title of the analysis
    params: MotifParams
        Dataclass storing dirichlet_alpha, number_of_motifs, \
        length_of_motifs_min, length_of_motifs_max, alphabet \
        and motif_files
    rng: np.random.Generator
        Random generator for length (uniform from integeres) \
        and motif (Dirichlet) sampling
    reader: Reader
        File reader class to read in motifs if necessary
    writer: Writer
        instance of the writer class
    motifs: Motifs
        Data class for motifs with names (key) and PPM, alphabet and ids
    motif_lengths: List[int]
        The number of positions in each motif
    """

    def __init__(
            self,
            params: MotifParams,
            rng: np.random.Generator,
            reader: Reader,
            writer: Writer) -> None:
        """Initialize simulator

        Parameters
        ----------
        params: MotifParams
            Dataclass storing dirichlet_alpha, number_of_motifs, \
            length_of_motifs_min, length_of_motifs_max, alphabet \
            and motif_files
        rng: np.random.Generator
            Random generator for length (uniform from integeres) \
            and motif (Dirichlet) sampling
        reader: Reader
            File reader class to read in motifs if necessary
        writer: Writer
            instance of the writer class
        """
        self.title = writer.get_title()
        self.rng = rng
        self.params = params
        self.motif_lengths = self.sample_lengths()
        self.reader = reader
        self.writer = writer
        self.motifs = None

    def get_motifs(self) -> Motifs:
        """ Get motifs

        Return
        ------
        motifs: Motifs
            Motifs dataclass with PWMs and metadata
        """
        return self.motifs

    def get_pwms(self) -> Dict[str, np.ndarray]:
        """ Get PWMs of motifs

        Return
        ------
        motif_dict: Dict[str, np.ndarray]
            Dictionary with the motif IDs and PWMs
        """
        return self.motifs.motifs

    def create_motifs(self) -> None:
        """ Controller function to read motifs from file or jaspar ID \
            if file not available or simulate if \
            no file nor ID are available """
        if self.params.motif_files is not None:
            self.read_motifs()
        else:
            self.simulate_motifs()
            self.writer.motif_to_meme(
                motifs=self.motifs.motifs,
                alphabet=self.params.m_alphabet,
                file_prefix="simulated_motifs")

    def sample_lengths(self) -> List[int]:
        """ Sample the length of a motif from uniform distribution

        Return
        ------
        lengths: List[int]
            The number of positions in each motif
        """
        motif_lengths = self.rng.integers(
            low=self.params.length_of_motifs_min,
            high=self.params.length_of_motifs_max,
            endpoint=True,
            size=self.params.number_of_motifs)
        return motif_lengths

    def simulate_one_motif(self, length: int) -> np.ndarray:
        """
        Generate motif in PPM format

        Parameters
        ----------
        length: int
            The number of positions in the motif

        Return
        ------
        motif: np.ndarray
            A single motif PWM in numpy array format
        """
        motif = self.rng.dirichlet(
            self.params.dirichlet_alpha,
            length)
        return motif

    def simulate_motifs(self) -> None:
        """ Generate motifs with name and PPM
        """
        motifs = {}
        for motif_idx in range(self.params.number_of_motifs):
            motif_name = self.title + "_motif_" + str(motif_idx)
            motifs[motif_name] = self.simulate_one_motif(
                length=self.motif_lengths[motif_idx])
        self.motifs = Motifs(
            motifs=motifs,
            alphabet=self.params.m_alphabet,
            alphabet_revcomp_pairs=self.params.m_alphabet_pairs)

    def read_motifs(self) -> None:
        """ Read  motifs from files in csv, jaspar or meme format
        """
        motifs, alphabet = self.reader.read_in_motifs(
            motif_files=self.params.motif_files,
            jaspar_db_version=self.params.jaspar_db_version)
        self.motifs = Motifs(
            motifs=motifs,
            alphabet=alphabet,
            alphabet_revcomp_pairs=self.params.m_alphabet_pairs)
