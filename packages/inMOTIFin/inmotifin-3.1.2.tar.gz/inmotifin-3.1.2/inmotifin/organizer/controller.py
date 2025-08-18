""" Controller class to organize the preparation and sampling """
from typing import List, Dict, Tuple, Any
import os
import numpy as np
from inmotifin.utils.paramsdata.basicparams import BasicParams
from inmotifin.utils.paramsdata.motifparams import MotifParams
from inmotifin.utils.paramsdata.dimerparams import DimerParams
from inmotifin.utils.paramsdata.groupparams import GroupParams
from inmotifin.utils.paramsdata.freqparams import FreqParams
from inmotifin.utils.paramsdata.backgroundparams import BackgroundParams
from inmotifin.utils.paramsdata.samplingparams import SamplingParams
from inmotifin.utils.paramsdata.positionparams import PositionParams
from inmotifin.utils.fileops.reader import Reader
from inmotifin.utils.fileops.writer import Writer
from inmotifin.modules.prepare.setupper import Setupper
from inmotifin.modules.prepare.dimerer import Dimerer
from inmotifin.modules.prepare.motifer import Motifer
from inmotifin.modules.prepare.backgrounder import Backgrounder
from inmotifin.modules.sample.sampler import Sampler
from inmotifin.modules.sample.inserter import Inserter
from inmotifin.modules.data.motif import Motifs
from inmotifin.modules.sample.motifinstancer import MotifInstancer
from inmotifin.modules.sample.inminscheme import InMOTIFinScheme
from inmotifin.organizer.summarizer import Summarizer


class Controller:
    """
    Organizer of preparation and sampling

    Class parameters
    ----------------
    reader: Reader
        File reader class to read in motifs if necessary
    writer: Writer
        instance of the writer class
    data_for_simulation: Dict[str, Any]
        Dictionary of simulated data passed for sampling
    summary: Dict[str, Dict[str, int]]
        Dictionary of summary information about the sampling
    rng: np.random.Generator
        Random generator for length (uniform from integeres) \
        and motif (Dirichlet) sampling
    """

    def __init__(self, basic_params: BasicParams) -> None:
        """
        Constructor

        Parameters
        ----------
        basic_params: BasicParams
            Dataclass storing title, workdir, and seed
        """
        self.writer = Writer(
            workdir=basic_params.workdir,
            title=basic_params.title)
        self.reader = Reader()
        self.data_for_simulation = {}
        self.rng = np.random.default_rng(basic_params.seed)
        self.summary = {}

    def create_dimers(self, dimer_params: DimerParams) -> None:
        """
        Option of creating dimers given input motifs and rules

        Parameters
        ----------
        dimer_params: DimerParams
            Dataclass storing motif_files, jaspar_db_version and \
            dimerisation_rule_path
        """
        my_dimerer = Dimerer(
            params=dimer_params,
            reader=self.reader,
            writer=self.writer,
            rng=self.rng)
        my_dimerer.create_dimers()

    def create_motifs(self, motif_params: MotifParams) -> None:
        """
        Option of creating motifs given input parameters

        Parameters
        ----------
        motif_params: MotifParams
            Dataclass storing dirichlet_alpha, number_of_motifs, \
            length_of_motifs_min, length_of_motifs_max, alphabet \
            and motif_files
        """
        motifer = Motifer(
            params=motif_params,
            rng=self.rng,
            reader=self.reader,
            writer=self.writer)
        motifer.create_motifs()

    def create_backgrounds(self, background_params: BackgroundParams) -> None:
        """
        Option of creating backgrounds given input parameters

        Parameters
        ----------
        background_params: BackgroundParams
            Dataclass storing alphabet, sequence length, sequence number, \
            b_alphabet_prior, background_files, to_shuffle \
            and number_of_shuffle
        """
        backgrounder = Backgrounder(
            params=background_params,
            reader=self.reader,
            writer=self.writer,
            rng=self.rng)
        backgrounder.create_backgrounds()

    def simulate_backgrounds(
            self,
            background_params: BackgroundParams,
            b_lengths: List[int] = None,
            b_numbers: List[int] = None) -> List[str]:
        """
        Simulate backgrounds with background parameters, \
            but can also create multiple different lengths

        Parameters
        ----------
        background_params: BackgroundParams
            Dataclass storing alphabet, sequence length, sequence number, \
            b_alphabet_prior, background_files, to_shuffle \
            and number_of_shuffle
        b_lengths: List[int]
            List of lenght of simulated backgrounds. Order should \
            match with b_numbers. If None, fetched from params data
        b_numbers: List[int]
            List of number of simulated backgrounds. Order should \
            match with b_lengths. If None, fetched from params data

        Return
        ------
        backgrounds: List[str]
            List of background sequences
        """
        backgrounder = Backgrounder(
            params=background_params,
            reader=self.reader,
            writer=self.writer,
            rng=self.rng)
        backgrounds = []
        for b_length, b_number in zip(b_lengths, b_numbers):
            backgrounds += backgrounder.simulate_backgrounds(
                b_length=b_length,
                b_number=b_number)
        return backgrounds

    def create_motif_in_seq(
            self,
            background_ids: List[str],
            background_dict: Dict[str, str],
            b_alphabets: Dict[str, str],
            b_alphabet_priors: Dict[str, np.ndarray],
            positions: List[Tuple[int]],
            motif_ids: List[str],
            motifs: Motifs,
            orientations: List[List[int]],
            to_replace: bool = True
            ) -> Tuple[Dict[str, str], Dict[str, np.ndarray]]:
        """
        Add motif instances to specific positions into specific backgrounds

        Parameters
        ----------
        background_ids: List[str]
            List of background IDs in order of insertion
        background_dict: Dict[str, str]
            Dictionary of backgound IDs and sequences
        b_alphabets: Dict[str, str]
            Dictionary of background alphabet
        b_alphabet_priors: Dict[str, np.ndarray]
            Dictionary of background alphabet prior probabilities
        positions: List[List[Tuple[int]]]
            List of list of position tuples in order of insertion per \
            sequence and per motif in the inner list
        motif_ids: List[List[str]]
            List of list of motif IDs in order of insertion per sequence \
            and per position in the inner list.
        motifs: Motifs
            Data class for motifs with names (key), PPM, alphabet and \
            alphabet pairs
        orientations: List[List[int]]
            List of list of motif instance orientations per sequence \
            and per motif in the inner list.
        to_replace: bool
            Whether to replace backgorund bases with motif instance. \
            Alternative is to insert between existing bases. Default: True

        Return
        ------
        motif_in_sequences: Dict[str, str]
            Dictionary of sequence ids (with background, motif, position, \
            and orientation) and corresponding sequences with motifs in
        probabilistic_motif_in_sequences: Dict[str, np.ndarray]
            Dictionary of sequence ids (with background, motif, position, \
            and orientation) and corresponding probabilities of letters in \
            sequences with motifs in
        """
        comp0 = len(positions) != len(motif_ids)
        comp1 = len(positions) != len(background_ids)
        comp2 = len(positions) != len(orientations)
        if comp0 or comp1 or comp2:
            message = "Positions, motif ids and backgrounds ids should be "
            message += "of the same length. They are positions: "
            message += f"{len(positions)}, motif_ids: {len(motif_ids)}, "
            message += f"background_ids: {len(background_ids)}, "
            message += f"orientations: {len(orientations)}"
            print(message)
            raise AssertionError

        inserter = Inserter(to_replace=to_replace)
        instancer = MotifInstancer(
            motifs=motifs,
            rng=self.rng)

        full_zip = zip(
            background_ids,
            motif_ids,
            positions,
            orientations)
        motif_in_sequences = {}
        probabilistic_motif_in_sequences = {}
        for bck, mot_list, pos_list, orient_list in full_zip:
            seq_name = bck + "_" + "_".join(mot_list) + "_"
            seq_name += "_".join(
                [str(p[0]) + ":" + str(p[1]) for p in pos_list])
            seq_name += "_" + "_".join([str(ori) for ori in orient_list])
            motif_instances = instancer.sample_instances(
                motif_idx_list=mot_list,
                orientations=orient_list)
            motif_in_seq = inserter.generate_motif_in_sequence(
                sequence=background_dict[bck],
                motif_instances=motif_instances,
                positions=pos_list)
            motif_in_sequences[seq_name] = motif_in_seq
            prob_motif_in_seq = \
                inserter.generate_probabilistic_motif_in_sequence(
                    sequence=background_dict[bck],
                    b_alphabet=b_alphabets[bck],
                    b_alphabet_prior=b_alphabet_priors[bck],
                    motifs=motifs,
                    motif_ids=mot_list,
                    orientation_list=orient_list,
                    positions=pos_list)
            probabilistic_motif_in_sequences[seq_name] = prob_motif_in_seq

        return motif_in_sequences, probabilistic_motif_in_sequences

    def mask_motif_in_seq(
            self,
            seq_with_motif: List[str],
            positions: List[Tuple[int]],
            mask_alphabet: str,
            mask_alphabet_prior: np.array) -> List[str]:
        """
        Mask motif instances with background-like sequences

        Parameters
        ----------
        seq_with_motif: List[str]
            List of sequences with motifs in order of positions of masking
        positions: List[List[Tuple[int]]]
            List of list of position tuples in order of masking per \
            sequence and per motif in the inner list
        mask_alphabet: str
            Alphabet of masking
        mask_alphabet_prior: np.array
            Array of probabilties of each letter in the alphabet of masking

        Return
        ------
        masked_sequences: List[str]
            List of sequences from which the motifs are masked out
        """
        bckg_params = BackgroundParams(
            b_alphabet=mask_alphabet,
            b_alphabet_prior=mask_alphabet_prior,
            number_of_backgrounds=1,
            length_of_backgrounds=1,
            background_files=None,
            shuffle="none",
            number_of_shuffle=None)
        inserter = Inserter(to_replace=True)
        masked_sequences = []
        for bck, pos_list in zip(seq_with_motif, positions):
            b_lengths = [pos[1]-pos[0]+1 for pos in pos_list]
            b_numbers = [1]*len(b_lengths)
            seq_masks = self.simulate_backgrounds(
                background_params=bckg_params,
                b_lengths=b_lengths,
                b_numbers=b_numbers)
            masked_seq = inserter.generate_motif_in_sequence(
                sequence=bck,
                motif_instances=seq_masks,
                positions=pos_list)
            masked_sequences.append(masked_seq)
        return masked_sequences

    def setup_simulation(
            self,
            motif_params: MotifParams,
            background_params: BackgroundParams,
            group_params: GroupParams,
            freq_params: FreqParams) -> None:
        """
        Create data for sampling

        Parameters
        ----------
        motif_params: MotifParams
            Dataclass storing dirichlet_alpha, number_of_motifs, \
            length_of_motifs_min, length_of_motifs_max, alphabet \
            and motif_files
        background_params: BackgroundParams
            Dataclass storing alphabet, sequence length, sequence number, \
            b_alphabet_prior, background_files, to_shuffle \
            and number_of_shuffle
        group_params: groupParams
            Dataclass storing number_of_groups, max_group_size, \
            group_size_binom_p and group_motif_assignment_file
        freq_params: FreqParams
            Dataclass storing group_frequency_type, group_frequency_range, \
            motif_frequency_type, motif_frequency_range, group_freq_file and \
            motif_freq_file
        """
        setupper = Setupper(
            reader=self.reader,
            writer=self.writer,
            motif_params=motif_params,
            background_params=background_params,
            group_params=group_params,
            frequency_params=freq_params,
            rng=self.rng)
        self.data_for_simulation["motifs"] = setupper.create_motifs()
        self.data_for_simulation["backgrounds"] = setupper.create_backgrounds()
        self.data_for_simulation["groups"] = setupper.create_groups()
        self.data_for_simulation["frequencies"] = setupper.create_frequencies()

    def run_sampling(
            self,
            sampling_params: SamplingParams,
            positions_params: PositionParams) -> Tuple[Any]:
        """
        Run main simulation module and save output

        Parameters
        ----------
        sampling_params: SamplingParams
            Data class with sampling parameters
        positions_params: PositionParams
            Data class with positioning parameters

        Return
        ------
        sampled_data: Tuple[Any]
            Tuple containing dagsim_graph, data, and no_motif_seq
        """
        dag_name = self.writer.get_outfolder()
        sampler = Sampler(
            sampling_params=sampling_params,
            position_params=positions_params,
            data_for_simulation=self.data_for_simulation,
            reader=self.reader,
            rng=self.rng)
        my_sim = InMOTIFinScheme(
            dag_name=os.path.join(
                dag_name,
                self.writer.title + "_dagsim_table"),
            sampler=sampler,
            number_of_motif_in_seq=sampling_params.number_of_motif_in_seq)
        dagsim_graph, data = my_sim.run_sampling()
        no_motif_seq = sampler.get_backgrounds(
            num_backgrounds=sampling_params.number_of_no_motif_in_seq)
        return dagsim_graph, data, no_motif_seq

    def save_outputs(
            self,
            dagsim_graph,
            data,
            no_motif_seq: List[str],
            to_draw: bool) -> None:
        """
        Save outputs of simulation into files

        Parameters
        ----------
        dagsim_graph
            Graph output from DagSim
        data: Dict[]
            Dictionary of sampled data
        no_motif_seq: List[str]
            List of sequences without motifs
        to_draw: bool
            Whether to draw dagsim_graph or not
        """
        if to_draw:
            dagsim_graph.draw()
        self.writer.save_dagsim_data(
            dagsim_data=data,
            nomotif_in_seq=no_motif_seq)
        summarizer = Summarizer(
            dagsim_data=data,
            no_motif_seq=no_motif_seq,
            writer=self.writer)
        self.summary = summarizer.summarize()

    def run_inmotifin(
            self,
            motif_params: MotifParams,
            background_params: BackgroundParams,
            group_params: GroupParams,
            freq_params: FreqParams,
            sampling_params: SamplingParams,
            positions_params: PositionParams) -> None:
        """
        Prepare and sample

        Parameters
        ----------
        motif_params: MotifParams
            Dataclass storing dirichlet_alpha, number_of_motifs, \
            length_of_motifs_min, length_of_motifs_max, alphabet \
            and motif_files
        background_params: BackgroundParams
            Dataclass storing alphabet, sequence length, sequence number, \
            b_alphabet_prior, background_files, to_shuffle \
            and number_of_shuffle
        group_params: groupParams
            Dataclass storing number_of_groups, max_group_size, \
            group_size_binom_p and group_motif_assignment_file
        freq_params: FreqParams
            Dataclass storing group_frequency_type, group_frequency_range, \
            motif_frequency_type, motif_frequency_range, group_freq_file and \
            motif_freq_file
        sampling_params: SamplingParams
            Data class with sampling parameters
        positions_params: PositionParams
            Data class with positioning parameters
        """
        self.setup_simulation(
            motif_params=motif_params,
            background_params=background_params,
            group_params=group_params,
            freq_params=freq_params)
        dagsim_graph, data, no_motif_seq = self.run_sampling(
            sampling_params=sampling_params,
            positions_params=positions_params)
        self.save_outputs(
            dagsim_graph=dagsim_graph,
            data=data,
            no_motif_seq=no_motif_seq,
            to_draw=sampling_params.to_draw)
