""" Data storage for sampling parameters """
from dataclasses import dataclass, field


@dataclass
class SamplingParams:
    """ Class for keeping track of parameters for sampling

    Class parameters
    ----------------
    to_draw: bool
        Whether to draw the DAG of the sampling, default is False
    number_of_sequences: int
        Number of sequences to generate, default is 100
    percentage_no_motif: float
        Percentage of sequences without motif, default is 0
    orientation_probability: float
        Probability of orientation for the motif, default is 0.5
    num_groups_per_sequence: int
        Number of groups per sequence, default is 1
    n_instances_per_sequence: int
        Number of instances per sequence, default is 1
    lambda_n_instances_per_sequence: int
        Lambda for the number of instances per sequence when Poisson \
        distribution is used
    """
    to_draw: bool
    number_of_sequences: int
    percentage_no_motif: float
    orientation_probability: float
    num_groups_per_sequence: int
    n_instances_per_sequence: int
    lambda_n_instances_per_sequence: int
    number_of_motif_in_seq: int = field(init=False)
    number_of_no_motif_in_seq: int = field(init=False)

    def __post_init__(self):
        """ Set defaults, validate values, and calculate number \
            of motif-in- and no-motif-in- sequences
        """
        if self.to_draw is None:
            self.to_draw = False
        if self.number_of_sequences is None:
            self.number_of_sequences = 100
        if self.percentage_no_motif is None:
            self.percentage_no_motif = 0
        if 0 > self.percentage_no_motif > 100:
            raise ValueError(f"Percentage value should be between 0 and 100. \
                Currently it is {self.percentage_no_motif}")
        if 0 < self.percentage_no_motif < 1:
            message = "Percentage value is less than 1, note that X '%'"
            message += "expected, so it is further divided by 100."
            print(message)
        if self.orientation_probability is None:
            self.orientation_probability = 0.5
        if self.num_groups_per_sequence is None:
            self.num_groups_per_sequence = 1
        if self.n_instances_per_sequence is None:
            if self.lambda_n_instances_per_sequence is None:
                self.n_instances_per_sequence = 1
        self.number_of_no_motif_in_seq = \
            int(self.number_of_sequences * self.percentage_no_motif / 100)
        self.number_of_motif_in_seq = \
            self.number_of_sequences - self.number_of_no_motif_in_seq
