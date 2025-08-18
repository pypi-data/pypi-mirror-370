""" File for functions overwriting config file input"""
import os
import yaml
from yaml.loader import SafeLoader

from inmotifin.utils.paramsdata.basicparams import BasicParams
from inmotifin.utils.paramsdata.motifparams import MotifParams
from inmotifin.utils.paramsdata.backgroundparams import BackgroundParams
from inmotifin.utils.paramsdata.groupparams import GroupParams
from inmotifin.utils.paramsdata.freqparams import FreqParams
from inmotifin.utils.paramsdata.samplingparams import SamplingParams
from inmotifin.utils.paramsdata.positionparams import PositionParams


def read_config(ctx, config):
    """ Helper function to read config and initialize ctx.default_map"""
    if config is not None:
        if os.path.exists(config):
            with open(config, 'r', encoding='utf-8') as config_file:
                config = yaml.load(config_file, Loader=SafeLoader)
            ctx.default_map = config
    else:
        ctx.default_map = {}
    return ctx


def assign_basic_params(
        ctx,
        title,
        workdir,
        seed):
    """ Helper function to overwrite basic params in config
    when applicable """
    if title is not None:
        ctx.default_map['title'] = title
    if workdir is not None:
        ctx.default_map['workdir'] = workdir
    if "workdir" not in ctx.default_map:
        ctx.default_map['workdir'] = None
    if seed is not None:
        ctx.default_map['seed'] = seed
    if "seed" not in ctx.default_map:
        ctx.default_map['seed'] = None
    basic_params = BasicParams(
        title=ctx.default_map['title'],
        workdir=ctx.default_map['workdir'],
        seed=ctx.default_map['seed'])
    return ctx, basic_params


def assign_motif_params(
        ctx,
        dirichlet_alpha,
        num_motifs,
        m_length_min,
        m_length_max,
        m_alphabet,
        m_alphabet_pairs,
        motif_files,
        jaspar_db_version):
    """ Helper function to overwrite motif params in config
    when applicable """
    if dirichlet_alpha is not None:
        alpha_list = list(dirichlet_alpha.split(','))
        ctx.default_map['dirichlet_alpha'] = alpha_list
    if "dirichlet_alpha" not in ctx.default_map:
        ctx.default_map['dirichlet_alpha'] = None
    if num_motifs is not None:
        ctx.default_map['num_motifs'] = num_motifs
    if "num_motifs" not in ctx.default_map:
        ctx.default_map['num_motifs'] = None
    if m_length_min is not None:
        ctx.default_map['m_length_min'] = m_length_min
    if "m_length_min" not in ctx.default_map:
        ctx.default_map['m_length_min'] = None
    if m_length_max is not None:
        ctx.default_map['m_length_max'] = m_length_max
    if "m_length_max" not in ctx.default_map:
        ctx.default_map['m_length_max'] = None
    if m_alphabet is not None:
        ctx.default_map['m_alphabet'] = m_alphabet
    if "m_alphabet" not in ctx.default_map:
        ctx.default_map['m_alphabet'] = None
    if m_alphabet_pairs is not None:
        ctx.default_map['m_alphabet_pairs'] = m_alphabet_pairs
    if "m_alphabet_pairs" not in ctx.default_map:
        ctx.default_map['m_alphabet_pairs'] = None
    if motif_files is not None:
        mfiles_list = list(motif_files.split(','))
        ctx.default_map['motif_files'] = mfiles_list
    if "motif_files" not in ctx.default_map:
        ctx.default_map['motif_files'] = None
    if jaspar_db_version is not None:
        ctx.default_map['jaspar_db_version'] = jaspar_db_version
    if "jaspar_db_version" not in ctx.default_map:
        ctx.default_map['jaspar_db_version'] = None
    if ctx.default_map["m_alphabet_pairs"] is not None:
        m_alphabet_pairs_dict = dict(
            i.split(':') for i in
            ctx.default_map["m_alphabet_pairs"].split(','))
    else:
        m_alphabet_pairs_dict = None

    motif_params = MotifParams(
        dirichlet_alpha=ctx.default_map['dirichlet_alpha'],
        number_of_motifs=ctx.default_map['num_motifs'],
        length_of_motifs_min=ctx.default_map['m_length_min'],
        length_of_motifs_max=ctx.default_map['m_length_max'],
        m_alphabet=ctx.default_map['m_alphabet'],
        m_alphabet_pairs=m_alphabet_pairs_dict,
        motif_files=ctx.default_map['motif_files'],
        jaspar_db_version=ctx.default_map['jaspar_db_version'])
    return ctx, motif_params


def assign_background_params(
        ctx,
        num_backgrounds,
        b_alphabet,
        b_alphabet_prior,
        b_length,
        background_files,
        shuffle,
        num_shuffle):
    """ Helper function to overwrite background params in config
    when applicable """
    if b_alphabet is not None:
        ctx.default_map['b_alphabet'] = b_alphabet
    if "b_alphabet" not in ctx.default_map:
        ctx.default_map['b_alphabet'] = None
    if b_alphabet_prior is not None:
        b_alphabet_prior_list = [
            float(bap) for bap in list(b_alphabet_prior.split(','))]
        ctx.default_map['b_alphabet_prior'] = b_alphabet_prior_list
    if "b_alphabet_prior" not in ctx.default_map:
        ctx.default_map['b_alphabet_prior'] = None
    if num_backgrounds is not None:
        ctx.default_map['num_backgrounds'] = num_backgrounds
    if "num_backgrounds" not in ctx.default_map:
        ctx.default_map['num_backgrounds'] = None
    if b_length is not None:
        ctx.default_map['b_length'] = b_length
    if "b_length" not in ctx.default_map:
        ctx.default_map['b_length'] = None
    if background_files is not None:
        bfiles_list = list(background_files.split(","))
        ctx.default_map['background_files'] = bfiles_list
    if "background_files" not in ctx.default_map:
        ctx.default_map['background_files'] = None
    if shuffle is not None:
        ctx.default_map['shuffle'] = shuffle
    if "shuffle" not in ctx.default_map:
        ctx.default_map['shuffle'] = None
    if num_shuffle is not None:
        ctx.default_map['num_shuffle'] = num_shuffle
    if "num_shuffle" not in ctx.default_map:
        ctx.default_map['num_shuffle'] = None

    bakground_params = BackgroundParams(
        b_alphabet=ctx.default_map['b_alphabet'],
        b_alphabet_prior=ctx.default_map['b_alphabet_prior'],
        number_of_backgrounds=ctx.default_map['num_backgrounds'],
        length_of_backgrounds=ctx.default_map['b_length'],
        background_files=ctx.default_map['background_files'],
        shuffle=ctx.default_map['shuffle'],
        number_of_shuffle=ctx.default_map['num_shuffle'])
    return ctx, bakground_params


def assign_group_freq_params(
        ctx,
        num_groups,
        max_group_size,
        group_size_p,
        group_motif_assignment_file,
        group_freq_type,
        group_freq_range,
        motif_freq_type,
        motif_freq_range,
        concentration_factor,
        group_group_type,
        group_freq_file,
        motif_freq_file,
        group_group_file):
    """ Helper function to overwrite group and frequency params \
        in config when applicable """
    if num_groups is not None:
        ctx.default_map['num_groups'] = num_groups
    if "num_groups" not in ctx.default_map:
        ctx.default_map['num_groups'] = None
    if max_group_size is not None:
        ctx.default_map['max_group_size'] = max_group_size
    if "max_group_size" not in ctx.default_map:
        ctx.default_map['max_group_size'] = None
    if group_size_p is not None:
        ctx.default_map['group_size_p'] = group_size_p
    if "group_size_p" not in ctx.default_map:
        ctx.default_map['group_size_p'] = None
    if group_motif_assignment_file is not None:
        ctx.default_map['group_motif_assignment_file'] = \
                group_motif_assignment_file
    if "group_motif_assignment_file" not in ctx.default_map:
        ctx.default_map['group_motif_assignment_file'] = None

    group_params = GroupParams(
        number_of_groups=ctx.default_map['num_groups'],
        max_group_size=ctx.default_map['max_group_size'],
        group_size_binom_p=ctx.default_map['group_size_p'],
        group_motif_assignment_file=ctx.default_map[
            'group_motif_assignment_file'])

    if group_freq_type is not None:
        ctx.default_map['group_freq_type'] = group_freq_type
    if "group_freq_type" not in ctx.default_map:
        ctx.default_map['group_freq_type'] = None
    if group_freq_range is not None:
        ctx.default_map['group_freq_range'] = group_freq_range
    if "group_freq_range" not in ctx.default_map:
        ctx.default_map['group_freq_range'] = None
    if motif_freq_type is not None:
        ctx.default_map['motif_freq_type'] = motif_freq_type
    if "motif_freq_type" not in ctx.default_map:
        ctx.default_map['motif_freq_type'] = None
    if motif_freq_range is not None:
        ctx.default_map['motif_freq_range'] = motif_freq_range
    if "motif_freq_range" not in ctx.default_map:
        ctx.default_map['motif_freq_range'] = None
    if concentration_factor is not None:
        ctx.default_map['concentration_factor'] = concentration_factor
    if "concentration_factor" not in ctx.default_map:
        ctx.default_map['concentration_factor'] = None
    if group_group_type is not None:
        ctx.default_map['group_group_type'] = group_group_type
    if "group_group_type" not in ctx.default_map:
        ctx.default_map['group_group_type'] = None
    if group_freq_file is not None:
        ctx.default_map['group_freq_file'] = group_freq_file
    if "group_freq_file" not in ctx.default_map:
        ctx.default_map['group_freq_file'] = None
    if motif_freq_file is not None:
        ctx.default_map['motif_freq_file'] = motif_freq_file
    if "motif_freq_file" not in ctx.default_map:
        ctx.default_map['motif_freq_file'] = None
    if group_group_file is not None:
        ctx.default_map['group_group_file'] = group_group_file
    if "group_group_file" not in ctx.default_map:
        ctx.default_map['group_group_file'] = None

    freq_params = FreqParams(
        group_frequency_type=ctx.default_map['group_freq_type'],
        group_frequency_range=ctx.default_map['group_freq_range'],
        motif_frequency_type=ctx.default_map['motif_freq_type'],
        motif_frequency_range=ctx.default_map['motif_freq_range'],
        group_group_type=ctx.default_map['group_group_type'],
        concentration_factor=ctx.default_map['concentration_factor'],
        group_freq_file=ctx.default_map['group_freq_file'],
        motif_freq_file=ctx.default_map['motif_freq_file'],
        group_group_file=ctx.default_map['group_group_file'])

    return ctx, group_params, freq_params


def assign_position_sampling_params(
        ctx,
        position_type,
        position_means,
        position_variances,
        num_motif_in_seq,
        pc_no_motif,
        to_replace,
        orientation_prob,
        num_groups_per_seq,
        n_instances_per_sequence,
        n_instances_per_sequence_l,
        to_draw):
    """ Helper function to overwrite positioning and sampling params \
        in config when applicable """
    if position_type is not None:
        ctx.default_map['position_type'] = position_type
    if "position_type" not in ctx.default_map:
        ctx.default_map['position_type'] = None
    if position_means is not None:
        position_means = list(position_means.split(','))
        ctx.default_map['position_means'] = [int(pm) for pm in position_means]
    if "position_means" not in ctx.default_map:
        ctx.default_map['position_means'] = None
    if position_variances is not None:
        position_variances = list(position_variances.split(','))
        ctx.default_map['position_variances'] = [
            float(pv) for pv in position_variances]
    if "position_variances" not in ctx.default_map:
        ctx.default_map['position_variances'] = None
    if to_replace:
        ctx.default_map['to_replace'] = True
    if "to_replace" not in ctx.default_map:
        ctx.default_map['to_replace'] = None

    gaussian = ctx.default_map['position_type'] == "gaussian"
    replacer = ctx.default_map['to_replace'] is True

    if gaussian and replacer:
        print(
            "Note: Replacement of background is disabled when gaussian \
            mode is selected. Insertion will happen instead.")

    positions_params = PositionParams(
        position_type=ctx.default_map['position_type'],
        to_replace=ctx.default_map['to_replace'],
        position_means=ctx.default_map['position_means'],
        position_variances=ctx.default_map['position_variances'])

    if to_draw:
        ctx.default_map['to_draw'] = True
    if "to_draw" not in ctx.default_map:
        ctx.default_map['to_draw'] = None
    if num_motif_in_seq is not None:
        ctx.default_map['num_motif_in_seq'] = num_motif_in_seq
    if "num_motif_in_seq" not in ctx.default_map:
        ctx.default_map['num_motif_in_seq'] = None
    if pc_no_motif is not None:
        ctx.default_map['pc_no_motif'] = pc_no_motif
    if "pc_no_motif" not in ctx.default_map:
        ctx.default_map['pc_no_motif'] = None
    if orientation_prob is not None:
        ctx.default_map['orientation_prob'] = orientation_prob
    if "orientation_prob" not in ctx.default_map:
        ctx.default_map['orientation_prob'] = None
    if num_groups_per_seq is not None:
        ctx.default_map['num_groups_per_sequence'] = \
            num_groups_per_seq
    if "num_groups_per_sequence" not in ctx.default_map:
        ctx.default_map['num_groups_per_sequence'] = None
    if n_instances_per_sequence is not None:
        ctx.default_map['n_instances_per_sequence'] = \
            n_instances_per_sequence
    if "n_instances_per_sequence" not in ctx.default_map:
        ctx.default_map['n_instances_per_sequence'] = None
    if n_instances_per_sequence_l is not None:
        ctx.default_map['lambda_n_instances_per_sequence'] = \
                n_instances_per_sequence_l
    if "lambda_n_instances_per_sequence" not in ctx.default_map:
        ctx.default_map['lambda_n_instances_per_sequence'] = None

    sampling_params = SamplingParams(
        to_draw=ctx.default_map['to_draw'],
        number_of_sequences=ctx.default_map['num_motif_in_seq'],
        percentage_no_motif=ctx.default_map['pc_no_motif'],
        orientation_probability=ctx.default_map['orientation_prob'],
        num_groups_per_sequence=ctx.default_map['num_groups_per_sequence'],
        n_instances_per_sequence=ctx.default_map[
            'n_instances_per_sequence'],
        lambda_n_instances_per_sequence=ctx.default_map[
            'lambda_n_instances_per_sequence'])

    return ctx, positions_params, sampling_params
