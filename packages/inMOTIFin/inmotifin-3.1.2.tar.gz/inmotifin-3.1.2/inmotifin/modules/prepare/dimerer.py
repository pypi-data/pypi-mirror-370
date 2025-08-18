""" Class to create dimer motifs given input """
from typing import List, Tuple
import numpy as np
from inmotifin.utils.mathutils import normalize_array
from inmotifin.modules.data.motif import Motifs
from inmotifin.utils.fileops.reader import Reader
from inmotifin.utils.fileops.writer import Writer
from inmotifin.utils.paramsdata.dimerparams import DimerParams


class Dimerer:
    """ Prepare dimers given two motifs and a distance

    Class parameters
    ----------------
    params: DimerParams
        Dataclass storing motif_files, jaspar_db_version and \
        dimerisation_rule_path
    dimer_rules: Dict[str, Tuple[List[str], List[int]]]
        Dictionary of IDs and tuple of motif ID and pairwise distances
    motifs: Motifs
        Data class for motifs with names (key) and PPM, alphabet and ids
    dimers: Motifs
        Data class for dimer motifs with names (key) and PPM, alphabet and ids
    reader: Reader
        File reader class to read in motifs and distances
    writer: Writer
        instance of the writer class
    rng: np.random.Generator
        Random generator for adding epsilon to the equal \
        probability of empty positions
    """

    def __init__(
            self,
            params: DimerParams,
            reader: Reader,
            writer: Writer,
            rng: np.random.Generator) -> None:
        """Initialize simulator

        Parameters
        ----------
        params: DimerParams
            Dataclass storing motif_files, jaspar_db_version and \
            dimerisation_rule_path
        reader: Reader
            File reader class to read in motifs and distances
        writer: Writer
            instance of the writer class
        rng: np.random.Generator
            Random generator for adding epsilon to the equal \
            probability of empty positions
        """
        self.reader = reader
        self.writer = writer
        self.params = params
        self.rng = rng
        self.motifs = None
        self.dimer_rules = None
        self.dimers = None

    def set_motifs(self, motifs: Motifs) -> None:
        """ Setter for motifs when run from within python

        Parameters
        ----------
        motifs: Motifs
            Instance of the Motifs dataclass
        """
        self.motifs = motifs

    def get_dimers(self) -> Motifs:
        """ Getter for dimers

        Return
        ------
        dimers: Motifs
            Data class for dimer motifs with names (key) and PPM, alphabet \
            and ids
        """
        if self.dimers is None:
            raise ValueError(
                "Missing dimers. Please run create_a_dimer() first.")

    def read_motifs(self) -> None:
        """ Read  motifs from files in csv, jaspar or meme format
        """
        motifs, alphabet = self.reader.read_in_motifs(
            motif_files=self.params.motif_files,
            jaspar_db_version=self.params.jaspar_db_version)
        self.motifs = Motifs(
            motifs=motifs,
            alphabet=alphabet,
            alphabet_revcomp_pairs=None)

    def read_dimer_rules(self) -> None:
        """ Read tsv of dimerisation rules """
        self.dimer_rules = self.reader.read_dimerisation_tsv(
            dimerisation_rule_path=self.params.dimerisation_rule_path)

    def create_a_dimer(
            self,
            dimer_parts: Tuple[List[str], List[int]],
            random_variance: float = 0.01) -> np.ndarray:
        """  Based on motifs and a rule create a dimer

        Parameters
        ----------
        dimer_parts: Tuple[List[str], List[int]]
            Tuple of motif IDs and corresponding distances between
        random_variance: float
            Magnitude of gaussian variance at the in-between positions

        Return
        ------
        dimer: np.ndarray
            Dimer motif in numpy array format
        """
        component_ids = dimer_parts[0]
        distances = dimer_parts[1]
        # initialize dimer with first motif
        dimer = self.motifs.motifs[component_ids[0]]
        for idx, motif_id in enumerate(component_ids[1:]):
            # get next motif
            component = self.motifs.motifs[motif_id]
            # fetch distances for between current motif and previous motif
            if idx < len(distances):
                # if not yet at the end, add filling or
                # adjust dimer end and motif beginning
                if distances[idx] > 0:
                    # positive distance: fill in with non-informative positions
                    inbetween = np.full(
                        (distances[idx], len(self.motifs.alphabet)),
                        1/len(self.motifs.alphabet))
                    inbetween += self.rng.normal(
                            0, random_variance,
                            size=inbetween.shape)
                    inbetween_norm = normalize_array(inbetween.T).T
                    component = np.concatenate(
                        [inbetween_norm, component],
                        axis=0)
                elif distances[idx] < 0:
                    # negative distance: take average of before / after
                    to_trim = distances[idx]
                    # get overlapping region
                    comp_overlap = component[:-to_trim]
                    dimer_overlap = dimer[to_trim:]
                    # remove beginning from motif
                    component = component[-to_trim:]
                    # remove end from dimer
                    dimer = dimer[:to_trim]
                    inbetween = np.mean(np.array(
                        [comp_overlap, dimer_overlap]),
                        axis=0)
                    component = np.concatenate([inbetween, component], axis=0)
                # if no distance in between, just add component
                dimer = np.concatenate([dimer, component], axis=0)
        return dimer

    def save_dimers(self) -> None:
        """ Save dimers in meme format """
        self.writer.motif_to_meme(
            motifs=self.dimers.motifs,
            alphabet=self.dimers.alphabet,
            file_prefix="dimer_motifs")

    def create_dimers(self) -> None:
        """ Main function to assemble and save dimers """
        self.read_motifs()
        self.read_dimer_rules()
        dimers_dict = {}
        for dimer_id, dimer_parts in self.dimer_rules.items():
            dimer = self.create_a_dimer(dimer_parts)
            dimers_dict[dimer_id] = dimer
        self.dimers = Motifs(
            motifs=dimers_dict,
            alphabet=self.motifs.alphabet,
            alphabet_revcomp_pairs=self.motifs.alphabet_revcomp_pairs)
        self.save_dimers()
