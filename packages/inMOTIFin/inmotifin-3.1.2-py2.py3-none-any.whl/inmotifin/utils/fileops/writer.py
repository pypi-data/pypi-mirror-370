""" Output class for methods writing in data from various formats """
from typing import List, Dict, Any
import os
import json
import numpy as np
import pandas as pd
from inmotifin.utils.dagsim_out_utils import (
    label_fasta_seq,
    extract_info_for_bed,
    extract_info_probabilistic_motif_in_seq)


class Writer:
    """IO methods for saving simulated motifs, groups and backgrounds

    Class parameters
    ----------------
    title: str
        Title of the analysis
    workdir: str
        Directory of the analysis
    outfolder: str
        A subfolder in the workdir with the same name as the title
    """

    def __init__(self, workdir: str, title: str) -> None:
        """ Constructor

        Parameters
        ----------
        title: str
            Title of the analysis
        workdir: str
            Directory of the analysis
        """
        self.workdir = workdir
        self.title = title
        self.outfolder = os.path.join(self.workdir, self.title)
        self.setup_dirs()

    def get_title(self) -> str:
        """ Getter for the analysis title

        Return
        ------
        title: str
            Title of the analysis
        """
        return self.title

    def get_outfolder(self) -> str:
        """ Getter for name of folder where output is saved

        Return
        ------
        outfolder: str
            A subfolder in the workdir with the same name as the title
        """
        return self.outfolder

    def setup_dirs(self) -> None:
        """ Create workfolder and outfolder if does not exist yet """
        os.makedirs(self.workdir, exist_ok=True)
        os.makedirs(self.outfolder, exist_ok=True)

    def list_to_file(
            self,
            data_list: List,
            filename: str,
            file_format: str = "txt") -> None:
        """Export data in list format to a file. One entry = one line

        Parameters
        ----------
        data_list:
            Any type of data in a list format
        filename:
            Output file name (without extension)
        file_format: str
            Format of the output file. Defaults to txt
        """
        filepath = os.path.join(
            self.outfolder,
            self.title + '_' + filename + '.' + file_format)
        with open(filepath, 'w+', encoding='utf-8') as out_file:
            for line in data_list:
                out_file.write(f"{line}\n")

    def pandas_to_tsv(self, dataframe: pd.DataFrame, filename: str) -> None:
        """ Write pandas dataframe to file

        Parameters
        ----------
        dataframe: pd.DataFrame
            Data to save
        filename: str
            File name prefix. TSV will be appended and saved to \
            outfolder with title prefix.
        """
        filepath = os.path.join(
            self.outfolder,
            self.title + '_' + filename + ".tsv")
        dataframe.to_csv(filepath, sep='\t')

    def dict_to_tsv(
            self,
            data_dict: Dict[Any, List[Any]], filename: str) -> None:
        """Export data in dict format to a tsv file. One entry = one line

        Parameters
        ----------
        data_dict Dict[Any, List[Any]]:
            any type of data in a dictionary format
        filename:
            File name prefix. TSV will be appended and saved to \
            outfolder with title prefix.
        """
        datalist = sorted(data_dict.items())
        outputs = []
        datalines = [f"{k}\t{v}" for k, v in datalist]
        removal_dict = {
            ord('['): None,
            ord(']'): None,
            ord(' '): None,
            ord('\''): None}
        for values in datalines:
            outputs.append(f"{values.translate(removal_dict)}")
        self.list_to_file(
            data_list=outputs,
            filename=filename,
            file_format="tsv")

    def dict_of_dict_to_json(
            self,
            counts_dict: Dict[str, Dict[str, int]],
            filename: str) -> None:
        """ Save counts dictionary to json

        Parameters
        ----------
        counts_dict: Dict[str, Dict[str, int]]:
            Dictionary of names, values and counts
        filename:
            Output file name prefix. Json will be appended and \
            saved to outfolder with title prefix.
        """
        filepath = os.path.join(
            self.outfolder,
            self.title + '_' + filename + ".json")
        with open(filepath, "w", encoding="utf-8") as outfile:
            json.dump(counts_dict, outfile, indent=4)

    def dict_to_fasta(
            self,
            seq_dict: Dict[str, str],
            filename: str) -> None:
        """Export data in list format to a fasta file. One entry = one line

        Parameters
        ----------
        seq_dict: Dict[str, str]:
            Sequence info and actual sequence in a dictionary format
        filename:
            Output file name prefix. Fa will be appended and \
            saved to outfolder with title prefix.
        """
        line_list = []
        for idx, seq in seq_dict.items():
            line_list.append(f">{idx}\n{seq}")
        self.list_to_file(
            data_list=line_list,
            filename=filename,
            file_format="fa")

    def motif_to_meme(
            self,
            motifs: Dict[str, np.ndarray],
            alphabet: str,
            file_prefix: str) -> None:
        """ Save motif position probability matrices in meme format

        Parameters
        ----------
        motifs: Dict[str, np.ndarray]
            the IDs and ppms of the simulated motifs
        alphabet: str
            Characters in the order of column assignment (eg ACGT)
        file_prefix: str
            Output file name prefix. Meme will be appended and \
            saved to outfolder with title prefix.
        """
        outputs = []
        header = "MEME version 4\n\n" + \
            f"ALPHABET= {alphabet}"
        outputs.append(header)
        removal_dict = {ord('['): None, ord(']'): None}

        for motif_id in motifs:
            motif_header = f"\nMOTIF {motif_id}\n" + \
                f"letter-probability matrix: alength= {len(alphabet)} " + \
                f"w= {motifs[motif_id].shape[0]}"
            outputs.append(motif_header)

            formatted_values = np.apply_along_axis(
                np.array2string,
                axis=1,
                arr=motifs[motif_id],
                formatter={'float_kind': lambda x: f"{x:.6f}"}
            )
            for values in formatted_values:
                outputs.append(f"{values.translate(removal_dict)}")

        self.list_to_file(
            data_list=outputs,
            filename=file_prefix,
            file_format="meme")

    def save_dictionary_with_numpy_to_npz(
            self,
            numpy_dict: Dict[str, np.ndarray],
            filename: str) -> None:
        """ Save dictionary with numpy arrays into npz format

        Parameters
        ----------
        numpy_dict: Dict[str, np.ndarray]
            Dictionary with string keys and any dimensional numpy arrays \
            as values
        filename: str
            File name which will get the .npz extension.
        """
        outfilepath = os.path.join(self.outfolder, filename + ".npz")
        np.savez(outfilepath, **numpy_dict)

    def motived_and_plain_to_fasta(
            self,
            dagsim_data: Dict[str, Any],
            no_motif_for_fasta: List[str]) -> None:
        """ Save fasta files with or without motived sequences.

        Parameters
        ----------
        dagsim_data: Dict[str, Any]
            dictionary from the Dagsim output
        no_motif_for_fasta: List[str]
            List of selected (not necessarily unique) background \
            IDs and sequences without inserted motif
        """
        filename = "final_sequences"
        output_dict = label_fasta_seq(
            dagsim_data=dagsim_data,
            no_motif_seq=no_motif_for_fasta)
        self.dict_to_fasta(
            seq_dict=output_dict,
            filename=filename)

    def data_to_bed(
            self,
            dagsim_data: Dict[str, Any]) -> None:
        """ Save bed files with motif coordinates.

        Parameters
        ----------
        dagsim_data: Dict[str, Any]
            dictionary from the Dagsim output
        """
        filename = "inserted_instances"
        line_list = extract_info_for_bed(dagsim_data=dagsim_data)
        self.list_to_file(
            data_list=line_list,
            filename=filename,
            file_format="bed")

    def save_dagsim_data(
            self,
            dagsim_data: Dict[str, Any],
            nomotif_in_seq: Dict[str, str]) -> None:
        """ Save dagsim data and unmotived sequences to bed and fasta files

        Parameters
        ----------
        dagsim_data: Dict[str, Any]
            dictionary from the Dagsim output
        nomotif_in_seq: Dict[str, str]
            List of background sequences without inserted motif
        """
        self.data_to_bed(dagsim_data=dagsim_data)
        prob_motif_in_seq = extract_info_probabilistic_motif_in_seq(
                dagsim_data=dagsim_data)
        self.save_dictionary_with_numpy_to_npz(
            numpy_dict=prob_motif_in_seq,
            filename=self.title + "_probabilistic_final_sequences")
        self.motived_and_plain_to_fasta(
            dagsim_data=dagsim_data,
            no_motif_for_fasta=nomotif_in_seq)
