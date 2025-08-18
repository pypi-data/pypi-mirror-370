"""Coordinator file for the simulation framework"""
from typing import Dict, Any, Tuple
import dagsim.base as ds
from inmotifin.modules.sample.sampler import Sampler


class InMOTIFinScheme:
    """ DagSim framework powering sampling for inMOTIFin scheme """

    def __init__(
            self,
            dag_name: str,
            sampler: Sampler,
            number_of_motif_in_seq: int) -> None:
        """Constructor for DagSim scheme
        Parameters
        ----------
        dag_name: str
            Name of the simulation to be used
        sampler: Sampler
            Sampler class which coordinates sampling of parts
        number_of_motif_in_seq: int
            Number of sequences with motifs to be inserted
        """
        self.dag_name = dag_name
        self.number_of_motif_in_seq = number_of_motif_in_seq
        # sampler module
        self.sampler = sampler
        # indeces of selected groups
        self.selected_groups = None
        # number of instances per sequence
        self.num_instances = None
        # indeces of selected motifs
        self.selected_motifs = None
        # motif instances
        self.instances = None
        # motif orientations
        self.orientations = None
        # positions
        self.positions = None
        # select background ID
        self.backgrounds = None
        # final sequence with inserted motifs
        self.motif_in_seq = None
        # probabilistic final sequence with inserted motifs
        self.prob_motif_in_seq = None
        # DAG scheme
        self.list_nodes = None
        self.my_graph = None

    def get_graph(self) -> ds.Graph:
        """Return graph attribute
        Return
        ------
        my_graph: ds.Graph
            Graph of the simulation (empty unless built already)
        """
        return self.my_graph

    def define_nodes(self) -> None:
        """Define nodes necessary for the simulation"""
        self.num_instances = ds.Node(
            name="num_instances",
            function=self.sampler.get_num_instances
        )
        self.selected_groups = ds.Node(
            name="selected_groups",
            function=self.sampler.select_groups
        )
        self.selected_motifs = ds.Node(
            name="selected_motifs",
            function=self.sampler.select_motifs,
            args=[self.selected_groups, self.num_instances]
        )
        self.orientations = ds.Node(
            name="orientations",
            function=self.sampler.select_orientations,
            args=[self.num_instances]
        )
        self.instances = ds.Node(
            name="instances",
            function=self.sampler.sample_instances,
            args=[self.selected_motifs, self.orientations]
        )
        self.backgrounds = ds.Node(
            name="backgrounds",
            function=self.sampler.get_background_id
        )
        self.positions = ds.Node(
            name="positions",
            function=self.sampler.get_positions,
            args=[self.backgrounds, self.instances]
        )
        self.motif_in_seq = ds.Node(
            name="motif_in_seq",
            function=self.sampler.get_motif_in_sequence,
            args=[
                self.backgrounds,
                self.instances,
                self.positions]
        )
        self.prob_motif_in_seq = ds.Node(
            name="prob_motif_in_seq",
            function=self.sampler.get_prob_motif_in_sequence,
            args=[
                self.backgrounds,
                self.selected_motifs,
                self.orientations,
                self.positions]
        )

    def define_dag(self) -> None:
        """Define the overall DAG scheme built from the nodes
        """
        self.list_nodes = [
            self.num_instances,
            self.selected_groups,
            self.selected_motifs,
            self.orientations,
            self.instances,
            self.backgrounds,
            self.positions,
            self.motif_in_seq,
            self.prob_motif_in_seq
            ]
        self.my_graph = ds.Graph(self.list_nodes, self.dag_name)

    def run_sampling(self) -> Tuple[ds.Graph, Dict[str, Any]]:
        """ Run main simulation module
        """
        self.define_nodes()
        self.define_dag()
        my_graph = self.get_graph()
        data = my_graph.simulate(
            num_samples=self.number_of_motif_in_seq,
            csv_name=self.dag_name)
        return my_graph, data
