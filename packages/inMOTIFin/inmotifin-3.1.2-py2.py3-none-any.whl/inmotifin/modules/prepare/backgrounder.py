""" Creating or importing backgrounds """
from typing import Dict, List
import numpy as np
from inmotifin.utils.baseutils import add_names_to_str
from inmotifin.utils.paramsdata.backgroundparams import BackgroundParams
from inmotifin.modules.data.background import Backgrounds
from inmotifin.modules.prepare.shuffler import Shuffler
from inmotifin.utils.fileops.reader import Reader
from inmotifin.utils.fileops.writer import Writer


class Backgrounder:
    """ Class to generate or read background sequences

    Class parameters
    ----------------
    title: str
        Title of the analysis
    params: BackgroundParams
        Dataclass storing alphabet, sequence length, sequence number, \
        b_alphabet_prior, background_files, to_shuffle \
        and number_of_shuffle
    backgrounds: Backgrounds
        Data class for backgrounds
    shuffler: Shuffler
        Class for shuffling background sequence
    reader: Reader
        File reader class to read in sequences if necessary
    writer: Writer
        instance of the writer class
    rng: np.random.Generator
        Random generator for sampling letters
    """

    def __init__(
            self,
            params: BackgroundParams,
            reader: Reader,
            writer: Writer,
            rng: np.random.Generator) -> None:
        """ Constructor

        Parameters
        ----------
        params: BackgroundParams
            Dataclass storing alphabet, sequence length, sequence number, \
            b_alphabet_prior, background_files, to_shuffle \
            and number_of_shuffle
        reader: Reader
            File reader class to read in sequences if necessary
        writer: Writer
            instance of the writer class
        rng: np.random.Generator
            Random generator for sampling letters
        """
        self.params = params
        self.reader = reader
        self.writer = writer
        self.rng = rng
        self.title = writer.get_title()
        self.backgrounds = None
        self.shuffler = Shuffler(
                number_of_shuffle=self.params.number_of_shuffle,
                rng=self.rng)

    def get_backgrounds(self) -> Backgrounds:
        """ Getter for simulated backgrounds

        Return
        -------
        backgrounds: Backgrounds
            Backgrounds dataclass with sequence and metadata
        """
        return self.backgrounds

    def get_backgrounds_seq(self) -> Dict[str, str]:
        """ Getter for simulated backgrounds

        Return
        -------
        backgrounds_seq: Dict[str, str]
            Dictionary with the background IDs and sequences
        """
        return self.backgrounds.backgrounds

    def shuffle_backgrounds(
            self,
            backgrounds: Dict[str, str]) -> Dict[str, str]:
        """
        Shuffle available backgrounds thus generate new ones

        Parameters
        ----------
        backgrounds: Dict[str, str]
            Dictionary with the background IDs and sequences

        Return
        -------
        backgrounds_seq: Dict[str, str]
            Dictionary with the shuffled background IDs and sequences
        """
        if self.params.shuffle.lower() == "none":
            return backgrounds
        if self.params.shuffle.lower() == "random_nucl_addon":
            shuffled = self.shuffler.shuffle_seq_random_nucleotide(
                backgrounds=backgrounds)
            backgrounds.update(shuffled)
        elif self.params.shuffle.lower() == "random_nucl_only":
            backgrounds = self.shuffler.shuffle_seq_random_nucleotide(
                backgrounds=backgrounds)
        else:
            print("Choose 'none', 'random_nucl_addon' or 'random_nucl_only'")
            raise NotImplementedError
        return backgrounds

    def simulate_backgrounds(
            self,
            b_length: int = None,
            b_number: int = None) -> List[str]:
        """Generates a dictionary of random sequences with ids

        Parameters
        ----------
        b_length: int
            Lenght of simulated backgrounds. If None, fetched from params data
        b_number: int
            Number of simulated backgrounds. If None, fetched from params data

        Return
        ------
        backgrounds: List[str]
            List of background sequences
        """
        if b_length is None:
            b_length = self.params.length_of_backgrounds
        if b_number is None:
            b_number = self.params.number_of_backgrounds
        backgrounds = []
        for _ in range(b_number):
            alphabet_to_list = list(self.params.b_alphabet)
            random_list = [
                self.rng.choice(
                    alphabet_to_list,
                    p=self.params.b_alphabet_prior,
                    replace=True)[0]
                for _ in range(b_length)
                ]
            random_sequence = "".join(random_list)
            backgrounds.append(random_sequence)

        return backgrounds

    def read_backgrounds(self) -> Dict[str, str]:
        """ Generates a dictionary of sequences with ids

        Return
        ------
        backgrounds: Dict[str, str]
            Dictionary of background sequences and IDs
        """
        backgrounds = self.reader.read_fasta(
            fasta_files=self.params.background_files)

        return backgrounds

    def create_backgrounds(self) -> None:
        """ Controller function to read backgrounds or simulate if \
            no file available """
        if self.params.background_files is not None:
            backgrounds = self.read_backgrounds()
            backgrounds = self.shuffle_backgrounds(backgrounds)
        else:
            backgrounds_list = self.simulate_backgrounds()
            backgrounds = add_names_to_str(
                seq_list=backgrounds_list,
                title=self.title)
            backgrounds = self.shuffle_backgrounds(backgrounds)
            self.writer.dict_to_fasta(
                seq_dict=backgrounds,
                filename="simulated_backgrounds")
        self.backgrounds = Backgrounds(
            backgrounds=backgrounds,
            b_alphabet=self.params.b_alphabet,
            b_alphabet_prior=self.params.b_alphabet_prior)
