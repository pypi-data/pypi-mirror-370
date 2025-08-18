""" Summarizer class to get stats from dagsim output """
from typing import Dict, Any, List
import itertools
from collections import Counter
import pandas as pd
from inmotifin.utils.fileops.writer import Writer


class Summarizer:
    """ Summerizer of dagsim output """

    def __init__(
            self,
            dagsim_data: Dict[str, Any],
            no_motif_seq: List[str],
            writer: Writer):
        """ Constructor for getting dagsim data"""
        self.data_df = pd.DataFrame(dagsim_data)
        self.writer = writer
        self.no_motif_seq = no_motif_seq
        self.occurrences = {}

    def summarize_list_occurrences(
            self,
            series: pd.Series) -> Dict[str, int]:
        """ Summarize the number of occurence of a given column\
            where values are lists"""
        element_list = list(
            itertools.chain.from_iterable(
                series.dropna().values))
        element_counts = dict(Counter(element_list))
        return element_counts

    def summarize_single_occurrences(
            self,
            series: pd.Series) -> Dict[str, int]:
        """ Summarize the number of occurence of a given column \
            where values are single elements"""
        element_counts = series.value_counts().to_dict()
        return element_counts

    def summarize_tuple_firsts(self, colname: str) -> Dict[str, int]:
        """ Count occcurrence of first element of a tuple"""
        first_el_series = self.data_df[colname].apply(
            lambda x: [tup[0] for tup in x])
        first_pos_counts = self.summarize_list_occurrences(
            series=first_el_series)
        return first_pos_counts

    def summarize_tuple_lengths(self, colname: str) -> Dict[str, int]:
        """ Count lengths as difference between 2nd and 1st element of tuple
        """
        length_series = self.data_df[colname].apply(
            lambda x: [tup[1] - tup[0] + 1 for tup in x])
        length_counts = self.summarize_list_occurrences(
            series=length_series)
        return length_counts

    def summarize_table(self) -> None:
        """ Make summaries of all columns of the table"""
        list_occ_cols = [
            "selected_groups",
            "orientations",
            "selected_motifs",
            "instances"]
        for lcolname in list_occ_cols:
            self.occurrences[lcolname] = self.summarize_list_occurrences(
                series=self.data_df[lcolname])
        single_occ_cols = [
            'backgrounds',
            "num_instances"]
        for scolname in single_occ_cols:
            self.occurrences[scolname] = self.summarize_single_occurrences(
                series=self.data_df[scolname])
        self.occurrences["position_starts"] = self.summarize_tuple_firsts(
            colname="positions")
        self.occurrences["motif_lengths"] = self.summarize_tuple_lengths(
            colname="positions")

    def add_no_motif_seq_counts(self) -> None:
        """ Add counts of backgrounds without motif"""
        nomotif_seq = []
        for seq_id_seq in self.no_motif_seq:
            nomotif_seq.append(seq_id_seq.split(',')[0])
        nmseq_counts = dict(Counter(nomotif_seq))
        self.occurrences["no_motif_backgrounds"] = nmseq_counts

    def save_occurrence_counts(self) -> None:
        """ Save counts to json """
        self.writer.dict_of_dict_to_json(
            counts_dict=self.occurrences,
            filename="occurrence_summaries")

    def summarize(self) -> Dict[str, Dict[str, int]]:
        """ Summarize simulation output"""
        self.summarize_table()
        self.add_no_motif_seq_counts()
        self.save_occurrence_counts()
        return self.occurrences
