"""Input class for methods reading motifs, groups and backgrounds"""
from typing import List, Dict, Tuple
import numpy as np
import pandas as pd
from Bio import SeqIO
from pyjaspar import jaspardb
from inmotifin.utils.baseutils import dict_of_list_to_dict
from inmotifin.utils.mathutils import convert_pfm_to_ppm


class Reader:
    """IO methods for reading motifs, groups and backgrounds
    """

    def read_fasta(self, fasta_files: List[str]) -> Dict[str, str]:
        """ Read fasta files into a dictionary of identifiers and sequences

        Parameters
        ----------
        fasta_files: List[str]
            Path to the files

        Return
        ------
        sequences: Dict[str, str]
            Dictionary of identifiers and sequences
        """
        sequences = {}
        for filename in fasta_files:
            reader = list(SeqIO.parse(filename, "fasta"))
            for seq_i in reader:
                bckg_id = seq_i.id
                if bckg_id not in sequences:
                    sequences[bckg_id] = [str(seq_i.seq)]
                else:
                    sequences[bckg_id].append(str(seq_i.seq))
        unique_id_sequences = dict_of_list_to_dict(sequences)
        return unique_id_sequences

    def convert_jaspardict_to_ppm(
            self,
            pyjaspar_out: Dict[str, List[float]]) -> np.ndarray:
        """ Convert dictionary of pyjaspar to numpy array

        Parameters
        ----------
        pyjaspar_out: Dict[str, List[float]]
            Dictionary in the form of {'A': [1,1,1], 'C':[1,1,1], etc}

        Return
        ------
        motif_ppm: np.ndarray
            Motif as ppm in numpy array format \
            (col: ACGT, row: value per position)
        """
        motif = np.array(list(pyjaspar_out.values())).T
        motif_ppm = convert_pfm_to_ppm(motif)
        return motif_ppm

    def fetch_motif_from_jaspar(
            self,
            mfile: str,
            jaspar_db_version: str = 'JASPAR2024'
            ) -> Tuple[Dict[str, np.ndarray], str]:
        """ Fetch  motifs from JASPAR database

        Parameters
        ----------
        mfile: str
            List of motif JASPAR IDs of interest
        jaspar_db_version: str
            Version of the JASPAR database. Defaults to JASPAR2024

        Return
        ------
        motifs: Dict[str, np.ndarray]
            Motifs with ID and ppm
        alphabet: str
            Letters of the input alphabet
        """
        jaspar_motifs = {}
        jaspar_motif_ids = []
        with open(mfile, encoding="utf=8") as infile:
            for line in infile:
                jaspar_motif_ids += line.strip().split(",")

        jdb_obj = jaspardb(release=jaspar_db_version)
        for motif_id in jaspar_motif_ids:
            motif_id = motif_id.strip()
            motif = jdb_obj.fetch_motif_by_id(motif_id)
            motif_dict = motif.counts
            jaspar_motifs[motif_id] = self.convert_jaspardict_to_ppm(
                pyjaspar_out=motif_dict)
            if set(motif_dict.keys()) != {'A', 'C', 'G', 'T'}:
                raise AssertionError(
                    f"JASPAR motif alphabet ({motif_dict.keys()}) \
                        does not match the expected ACGT")
        jaspar_alphabet = "ACGT"
        return jaspar_motifs, jaspar_alphabet

    def read_meme(self, mfile: str) -> Tuple[Dict[str, np.ndarray], str]:
        """ Read motif in meme

        Parameters
        ----------
        mfile: str
            Path to the file

        Return
        ------
        motifs_in: Dict[str, np.ndarray]
            Motifs with ID and ppm
        alphabet: str
            Letters of the input alphabet
        """
        motifs_in = {}
        alphabet = ""
        old_motif = False
        motif_id = ""
        motif_ppm = []
        expected_msg = "could not convert string to float: 'MOTIF'"

        with open(mfile, encoding="utf-8") as infile:
            for line in infile:
                alphabet_idx = line.find("ALPHABET=")
                if alphabet_idx != -1:
                    alphabet = line[alphabet_idx+10:].strip()
                motif_id_idx = line.find("MOTIF")
                if motif_id_idx != -1:
                    if old_motif:
                        # ensure that it is ppm
                        motifs_in[motif_id] = convert_pfm_to_ppm(
                            np.array(motif_ppm))
                    motif_id = line[motif_id_idx+6:].split()[0]
                    motif_ppm = []
                    old_motif = True
                width_idx = line.find("w=")
                if width_idx != -1:
                    motif_width = line[width_idx+3:].split()[0]
                    for _ in range(int(motif_width)):
                        motif_values = next(infile)
                        try:
                            values = [
                                float(val) for val in motif_values.strip(
                                    ).split()]
                        except ValueError as e:
                            if str(e) == expected_msg:
                                new_msg = "Incorrect motif width in "
                                new_msg += f"file {mfile}"
                                raise ValueError(new_msg) from e
                            raise e
                        motif_ppm.append(values)
            # ensure that it is ppm
            motifs_in[motif_id] = convert_pfm_to_ppm(np.array(motif_ppm))

        return motifs_in, alphabet

    def read_jaspar(self, mfile: str) -> Tuple[Dict[str, np.ndarray], str]:
        """ Read motif in jaspar format with Bio.motifs

        Parameters
        ----------
        mfile: str
            Path to the file

        Return
        ------
        motifs_in: Dict[str, np.ndarray]
            Motifs with ID and ppm
        alphabet: str
            Letters of the input alphabet
        """
        motifs_in = {}
        alphabet = 'ACGT'
        old_motif = False
        motif_id = ""
        motif_ppm = []
        with open(mfile, encoding="utf-8") as infile:
            for line in infile:
                if line.startswith(">"):
                    if old_motif:
                        # ensure that it is ppm
                        motifs_in[motif_id] = convert_pfm_to_ppm(
                            np.array(motif_ppm).T)
                    motif_id = line[1:].split()[0]
                    motif_ppm = []
                    old_motif = True
                else:
                    mvals = line.strip().split('[')[1].split(']')[0].split()
                    values = [float(val) for val in mvals]
                    motif_ppm.append(values)
        # adding last motif
        motifs_in[motif_id] = convert_pfm_to_ppm(np.array(motif_ppm).T)
        return motifs_in, alphabet

    def read_motif(
            self,
            mfile: str,
            jaspar_db_version: str = None) -> Dict[str, np.ndarray]:
        """ Read motif from inferred format

        Parameters
        ----------
        mfile: str
            Path to the file
        jaspar_db_version: str
            Version of the JASPAR database. Used when motif IDs are specified.\
            Defaults to None.

        Return
        ------
        motifs_in: Dict[str, np.ndarray]
            Motifs with ID and PWM
        """
        if mfile.endswith(".csv"):
            motifs_in, alphabet = self.fetch_motif_from_jaspar(
                mfile=mfile,
                jaspar_db_version=jaspar_db_version)
        elif mfile.endswith(".jaspar"):
            motifs_in, alphabet = self.read_jaspar(mfile=mfile)
        elif mfile.endswith(".meme"):
            motifs_in, alphabet = self.read_meme(mfile=mfile)
        else:
            raise AssertionError("Only meme, jaspar and csv (with jaspar IDs) \
                formats are supported")

        return motifs_in, alphabet

    def read_in_motifs(
            self,
            motif_files: List[str],
            jaspar_db_version: str
            ) -> Tuple[Dict[str, np.ndarray], str]:
        """ Select reader by identifying the format and read in motif

        Parameters
        ----------
        motif_files: List[str]
            List of files with motifs in jaspar or meme format
        jaspar_db_version: str
            Version of the JASPAR database. Used when motif IDs are specified.

        Return
        ------
        my_motifs: Dict[str, np.ndarray]
            Dictionary of motifs with ID as key and ppm as value
        alphabet: str
            Alphabet read from file. Only one is supported per run.
        """
        my_motifs = {}
        alphabets = []
        for mfile in motif_files:
            motifs_in, alphabet = self.read_motif(
                mfile=mfile,
                jaspar_db_version=jaspar_db_version)
            my_motifs.update(motifs_in)
            alphabets.append(alphabet)

        if len(set(alphabets)) > 1:
            raise ValueError(
                f"Multiple alphabets are found in the motif files: \
                    {alphabets}. Only one is supported per run.")
        alphabet = alphabets[0]

        return my_motifs, alphabet

    def read_dimerisation_tsv(
            self,
            dimerisation_rule_path: str
            ) -> Dict[str, Tuple[List[str], List[int]]]:
        """ Read tsv with two columns of comma separated lists: \
            List[str] and List[int]

        Parameters
        ----------
        dimerisation_rule_path: str
            Path to a tsv with two columns of comma separated lists: \
            List[str] and List[int]

        Return
        ------
        dimer_rules: Dict[str, Tuple[List[str], List[int]]]
            Dictionary of IDs and tuple of motif ID and pairwise distances
        """
        dimer_rules = {}
        with open(dimerisation_rule_path, "r", encoding="utf-8") as infile:
            for line in infile:
                line_info = line.strip().split("\t")
                motif_ids = line_info[0].split(",")
                motif_dist = [int(dval) for dval in line_info[1].split(",")]
                dimer_id = "_".join(motif_ids)
                if len(motif_ids) != len(motif_dist) + 1:
                    msg = "The number of motifs and distances do not "
                    msg += "correspond. There should be exactly one more "
                    msg += "motifs than distances.\n"
                    msg += f"motif ids: {motif_ids}, "
                    msg += f"motif distances: {motif_dist}"
                    raise AssertionError(msg)
                dimer_rules[dimer_id] = (motif_ids, motif_dist)
        return dimer_rules

    def read_twocolumn_tsv(
            self,
            twocolumns_tsv_path: str) -> Dict[str, List[str]]:
        """ Read tsv of two columns, second is a comma separated list \
            or a single value

        Parameters
        ----------
        twocolumns_tsv_path: str
            Path to a TSV file with two columns. First column must \
            have a single value.

        Return
        ------
        two_columns: Dict[str, List[str]]
            Dictionary of the values of the two columns, where the \
            key is the value of the first column and the value of \
            the dictionary is the value(s) of the second column.
        """
        two_columns = {}
        with open(twocolumns_tsv_path, "r", encoding="utf-8") as infile:
            for line in infile:
                line_info = line.strip().split("\t")
                col1 = line_info[0]
                col2 = line_info[1].split(",")
                two_columns[col1] = col2
        return two_columns

    def read_tsv_to_pandas(self, pandas_dftsv_path: str) -> pd.DataFrame:
        """ Read in tsv exported by pandas or tsv looking like that

        Parameters
        ----------
        pandas_dftsv_path: str
            Path to a TSV file with first column the index valued for \
            pandas dataframe

        Return
        ------
        df_from_tsv: pd.DataFrame
            Pandas dataframe from the provided TSV file
        """
        df_from_tsv = pd.read_csv(
            pandas_dftsv_path,
            sep="\t",
            index_col=0)
        return df_from_tsv
