"""Assign motifs to groups
author: Kata Ferenc
email: katalitf@uio.no
"""
from typing import List, Dict, Set
from itertools import chain
import numpy as np
from inmotifin.utils.paramsdata.groupparams import GroupParams
from inmotifin.modules.data.groups import Groups
from inmotifin.utils.fileops.reader import Reader
from inmotifin.utils.fileops.writer import Writer


class Grouper:
    """ Class to select motif-group

    Class parameters
    ----------------
    title: str
        Title of the analysis
    params: groupParams
        Dataclass storing number_of_groups, max_group_size, \
        group_size_binom_p and group_motif_assignment_file
    motif_ids: List[str]
        Motif IDs
    reader: Reader
        File reader class to read in sequences if necessary
    writer: Writer
        instance of the writer class
    groups: groups
        groups with names (key) and list of motifs within them
    rng: np.random.Generator
        Random generator for group sizes and motif sampling
    """

    def __init__(
            self,
            params: GroupParams,
            motif_ids: List[str],
            reader: Reader,
            writer: Writer,
            rng: np.random.Generator) -> None:
        """Constructor for group simulator

        Parameters
        ----------
        params: groupParams
            Dataclass storing number_of_groups, max_group_size, \
            group_size_binom_p and group_motif_assignment_file
        motif_ids: List[str]
            Motif IDs
        reader: Reader
            File reader class to read in sequences if necessary
        writer: Writer
            instance of the writer class
        rng: np.random.Generator
            Random generator for group sizes and motif sampling
        """
        self.title = writer.get_title()
        self.params = params
        self.rng = rng
        self.motif_ids = motif_ids
        self.reader = reader
        self.writer = writer
        self.groups = None

    def get_groups(self) -> Groups:
        """ Getter for groups

        Return
        ------
        groups: groups
            groups with names (key) and list of motifs within them
        """
        return self.groups

    def select_group_sizes_binomial(self) -> List[int]:
        """ Helper function to select sizes of groups

        Return
        ------
        adjusted_sizes: List[int]
            List of sizes of groups
        """
        # sample sizes from a binomial distribution
        group_sizes = self.rng.binomial(
            n=self.params.max_group_size,
            p=self.params.group_size_binom_p,
            size=self.params.number_of_groups)
        group_sizes_int = [int(group) for group in group_sizes]
        adjusted_sizes = []
        for group in group_sizes_int:
            # if group size is 0, set it to 1
            if group == 0:
                group = 1
            # group cannot be larger than the number of motifs
            adjusted_sizes.append(min(group, len(self.motif_ids)))
        if sum(adjusted_sizes) < len(self.motif_ids):
            print("Not all motifs can be assigned.")
            print("Consider raising group sizes.")

        return adjusted_sizes

    def membership_assignment(
            self,
            assignees: Set[str],
            group_sizes: List[int]) -> Dict[str, List[str]]:
        """General function to assign membership of one list to another

        Parameters
        ----------
        assignees: Set[str]
            Set of instances that should be assigned to groups
        group_sizes: List[int]
            List of sizes of groups

        Return
        ------
        group_assignee_membership: Dict[str, List[str]]
            Dictionary of memberships of assignees within groups
            Key: group id, Value: list of the id of the asignees
        """
        if max(group_sizes) > len(assignees):
            message = f"Not enough elements to assign ({len(assignees)}) "
            message += f"given the group size ({group_sizes})"
            raise AssertionError(message)
        group_assignee_membership = {}
        # sample assignees
        assignees_left = set(assignees.copy())
        for group_idx, group_size in enumerate(group_sizes):
            if group_size == 0:
                continue
            group_name = self.title + "_group_" + str(group_idx)
            group_assignee_membership[group_name] = []
            if len(assignees_left) < group_size:
                # if not enough assignees left, assign all to group
                # and reset them to all minus the latest selection
                group_assignee_membership[group_name] = list(assignees_left)
                group_size = group_size - len(assignees_left)
                assignees_left = set(assignees.copy()).difference(
                    assignees_left)
            selection = self.rng.choice(
                sorted(assignees_left),
                group_size,
                replace=False)
            selected_assignees = [str(mid) for mid in selection]
            group_assignee_membership[group_name] += selected_assignees
            group_assignee_membership[group_name].sort()
            assignees_left = assignees_left.difference(selected_assignees)

        if len(list(group_assignee_membership.keys())) == 0:
            message = "No groups contain motifs."
            message += "Consider increasing the size of groups"
            raise AssertionError(message)

        return group_assignee_membership

    def assign_motifs_to_groups(
            self,
            group_sizes: List[int]) -> Dict[str, List[str]]:
        """Assign each motif to a group

        Parameters
        ----------
        group_sizes: List[int]
            List of sizes of groups

        Return
        ------
        motif_group_membership: Dict[str, List[str]]
            Dictionary of the group IDs and the list of motifs within
        """
        motif_group_membership = {}
        if self.params.number_of_groups == 1:
            # if only one group, assign all motifs to that group
            group_name = self.title + "_group_" + str(0)
            motif_group_membership[group_name] = self.motif_ids
        else:
            # otherwise, assign motifs to groups
            motif_group_membership = self.membership_assignment(
                assignees=self.motif_ids,
                group_sizes=group_sizes)
        return motif_group_membership

    def simulate_groups(self) -> None:
        """ Simulate group sizes and memberships """
        if self.params.number_of_groups == 1:
            group_sizes = len(self.motif_ids)
        else:
            group_sizes = self.select_group_sizes_binomial()
        groups = self.assign_motifs_to_groups(
            group_sizes=group_sizes)
        self.groups = Groups(
            groups=groups)

    def read_groups(self) -> None:
        """ Read in group sizes and memberships from file"""
        groups = self.reader.read_twocolumn_tsv(
            twocolumns_tsv_path=self.params.group_motif_assignment_file)
        unique_motifs = set(list(chain.from_iterable(groups.values())))
        if len(unique_motifs) < len(self.motif_ids):
            print("Not all motifs can be assigned.")
            print("Consider raising group sizes.")

        self.groups = Groups(
            groups=groups)

    def create_groups(self) -> None:
        """ Create group sizes and memberships """
        if self.params.group_motif_assignment_file is not None:
            self.read_groups()
        else:
            self.simulate_groups()
            self.writer.dict_to_tsv(
                data_dict=self.groups.groups,
                filename="motif_group_membership")
