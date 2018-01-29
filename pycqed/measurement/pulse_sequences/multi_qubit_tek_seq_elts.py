import logging
import itertools
import numpy as np
from copy import deepcopy
import pycqed.measurement.waveform_control.sequence as sequence
from pycqed.utilities.general import add_suffix_to_dict_keys
from pycqed.measurement.pulse_sequences.standard_elements import \
    multi_pulse_elt, distort_and_compensate
import pycqed.measurement.randomized_benchmarking.randomized_benchmarking as rb
import pycqed.measurement.waveform_control.fluxpulse_predistortion as \
    fluxpulse_predistortion
from pycqed.measurement.pulse_sequences.single_qubit_tek_seq_elts import \
    get_pulse_dict_from_pars
import pycqed.instrument_drivers.meta_instrument.device_object as device

station = None
kernel_dir = 'kernels/'
# You need to explicitly set this before running any functions from this module
# I guess there are cleaner solutions :)
cached_kernels = {}


def avoided_crossing_spec_seq(operation_dict, q0, q1, RO_target,
                              verbose=False,
                              upload=True):

    seq_name = 'avoidec_crossing_spec'
    seq = sequence.Sequence(seq_name)
    station.pulsar.update_channel_settings()
    el_list = []
    sequencer_config = operation_dict['sequencer_config']

    # N.B. Identities not needed in all cases
    pulse_combinations = ['X180 '+q0, 'SpecPulse '+q1, 'RO '+RO_target]
    pulses = []
    for p in pulse_combinations:
        pulses += [operation_dict[p]]
    el = multi_pulse_elt(0, station, pulses, sequencer_config)
    el_list.append(el)
    seq.append_element(el, trigger_wait=True)
    if upload:
        station.pulsar.program_awgs(seq, *el_list, verbose=verbose)
    return seq, el_list


def two_qubit_off_on(q0_pulse_pars, q1_pulse_pars, RO_pars,
                     return_seq=False, verbose=False):

    seq_name = '2_qubit_OffOn_sequence'
    seq = sequence.Sequence(seq_name)
    station.pulsar.update_channel_settings()
    el_list = []
    # Create a dict with the parameters for all the pulses
    q0_pulses = add_suffix_to_dict_keys(
        get_pulse_dict_from_pars(q0_pulse_pars), ' q0')
    q1_pulses = add_suffix_to_dict_keys(
        get_pulse_dict_from_pars(q1_pulse_pars), ' q1')
    RO_dict = {'RO': RO_pars}

    pulse_dict = {}
    pulse_dict.update(q0_pulses)
    pulse_dict.update(q1_pulses)
    pulse_dict.update(RO_dict)

    # N.B. Identities not needed in all cases
    pulse_combinations = [['I q0', 'I q1', 'RO'],
                          ['X180 q0', 'I q1', 'RO'],
                          ['I q0', 'X180 q1', 'RO'],
                          ['X180 q0', 'X180 q1', 'RO']]

    for i, pulse_comb in enumerate(pulse_combinations):
        pulses = []
        for p in pulse_comb:
            pulses += [pulse_dict[p]]

        el = multi_pulse_elt(i, station, pulses)
        el_list.append(el)
        seq.append_element(el, trigger_wait=True)
    station.pulsar.program_awgs(seq, *el_list, verbose=verbose)
    if return_seq:
        return seq, el_list
    else:
        return seq_name


def three_qubit_off_on(q0_pulse_pars, q1_pulse_pars, q2_pulse_pars, RO_pars,
                       return_seq=False, verbose=False):

    seq_name = '3_qubit_OffOn_sequence'
    seq = sequence.Sequence(seq_name)
    station.pulsar.update_channel_settings()
    el_list = []
    # Create a dict with the parameters for all the pulses
    q0_pulses = add_suffix_to_dict_keys(
        get_pulse_dict_from_pars(q0_pulse_pars), ' q0')
    q1_pulses = add_suffix_to_dict_keys(
        get_pulse_dict_from_pars(q1_pulse_pars), ' q1')
    q2_pulses = add_suffix_to_dict_keys(
        get_pulse_dict_from_pars(q2_pulse_pars), ' q2')
    RO_dict = {'RO': RO_pars}

    pulse_dict = {}
    pulse_dict.update(q0_pulses)
    pulse_dict.update(q1_pulses)
    pulse_dict.update(q2_pulses)
    pulse_dict.update(RO_dict)

    # N.B. Identities not needed in all cases
    pulse_combinations = [['I q0', 'I q1', 'I q2', 'RO'],
                          ['X180 q0', 'I q1', 'I q2', 'RO'],
                          ['I q0', 'X180 q1', 'I q2', 'RO'],
                          ['X180 q0', 'X180 q1', 'I q2', 'RO'],
                          ['I q0', 'I q1', 'X180 q2', 'RO'],
                          ['X180 q0', 'I q1', 'X180 q2', 'RO'],
                          ['I q0', 'X180 q1', 'X180 q2', 'RO'],
                          ['X180 q0', 'X180 q1', 'X180 q2', 'RO']]

    for i, pulse_comb in enumerate(pulse_combinations):
        pulses = []
        for p in pulse_comb:
            pulses += [pulse_dict[p]]

        el = multi_pulse_elt(i, station, pulses)
        el_list.append(el)
        seq.append_element(el, trigger_wait=True)
    station.pulsar.program_awgs(seq, *el_list, verbose=verbose)
    if return_seq:
        return seq, el_list
    else:
        return seq_name


def four_qubit_off_on(q0_pulse_pars,
                      q1_pulse_pars,
                      q2_pulse_pars,
                      q3_pulse_pars,
                      RO_pars,
                      return_seq=False, verbose=False):

    seq_name = '4_qubit_OffOn_sequence'
    seq = sequence.Sequence(seq_name)
    station.pulsar.update_channel_settings()
    el_list = []
    # Create a dict with the parameters for all the pulses
    q0_pulses = add_suffix_to_dict_keys(
        get_pulse_dict_from_pars(q0_pulse_pars), ' q0')
    q1_pulses = add_suffix_to_dict_keys(
        get_pulse_dict_from_pars(q1_pulse_pars), ' q1')
    q2_pulses = add_suffix_to_dict_keys(
        get_pulse_dict_from_pars(q2_pulse_pars), ' q2')
    q3_pulses = add_suffix_to_dict_keys(
        get_pulse_dict_from_pars(q3_pulse_pars), ' q3')
    RO_dict = {'RO': RO_pars}

    pulse_dict = {}
    pulse_dict.update(q0_pulses)
    pulse_dict.update(q1_pulses)
    pulse_dict.update(q2_pulses)
    pulse_dict.update(q3_pulses)
    pulse_dict.update(RO_dict)

    # N.B. Identities not needed in all cases
    pulse_combinations = [['I q0', 'I q1', 'I q2', 'I q3', 'RO'],
                          ['X180 q0', 'I q1', 'I q2', 'I q3', 'RO'],
                          ['I q0', 'X180 q1', 'I q2', 'I q3', 'RO'],
                          ['X180 q0', 'X180 q1', 'I q2', 'I q3', 'RO'],
                          ['I q0', 'I q1', 'X180 q2', 'I q3', 'RO'],
                          ['X180 q0', 'I q1', 'X180 q2', 'I q3', 'RO'],
                          ['I q0', 'X180 q1', 'X180 q2',  'I q3', 'RO'],
                          ['X180 q0', 'X180 q1', 'X180 q2',  'I q3', 'RO'],
                          ['I q0', 'I q1', 'I q2', 'X180 q3', 'RO'],
                          ['X180 q0', 'I q1', 'I q2', 'X180 q3', 'RO'],
                          ['I q0', 'X180 q1', 'I q2', 'X180 q3', 'RO'],
                          ['X180 q0', 'X180 q1', 'I q2', 'X180 q3', 'RO'],
                          ['I q0', 'I q1', 'X180 q2', 'X180 q3', 'RO'],
                          ['X180 q0', 'I q1', 'X180 q2', 'X180 q3', 'RO'],
                          ['I q0', 'X180 q1', 'X180 q2',  'X180 q3', 'RO'],
                          ['X180 q0', 'X180 q1', 'X180 q2',  'X180 q3', 'RO']]

    for i, pulse_comb in enumerate(pulse_combinations):
        pulses = []
        for p in pulse_comb:
            pulses += [pulse_dict[p]]

        el = multi_pulse_elt(i, station, pulses)
        el_list.append(el)
        seq.append_element(el, trigger_wait=True)
    station.pulsar.program_awgs(seq, *el_list, verbose=verbose)
    if return_seq:
        return seq, el_list
    else:
        return seq_name


def five_qubit_off_on(q0_pulse_pars,
                      q1_pulse_pars,
                      q2_pulse_pars,
                      q3_pulse_pars,
                      q4_pulse_pars,
                      RO_pars,
                      return_seq=False, verbose=False):

    seq_name = '5_qubit_OffOn_sequence'
    seq = sequence.Sequence(seq_name)
    station.pulsar.update_channel_settings()
    el_list = []
    # Create a dict with the parameters for all the pulses
    q0_pulses = add_suffix_to_dict_keys(
        get_pulse_dict_from_pars(q0_pulse_pars), ' q0')
    q1_pulses = add_suffix_to_dict_keys(
        get_pulse_dict_from_pars(q1_pulse_pars), ' q1')
    q2_pulses = add_suffix_to_dict_keys(
        get_pulse_dict_from_pars(q2_pulse_pars), ' q2')
    q3_pulses = add_suffix_to_dict_keys(
        get_pulse_dict_from_pars(q3_pulse_pars), ' q3')
    q4_pulses = add_suffix_to_dict_keys(
        get_pulse_dict_from_pars(q4_pulse_pars), ' q4')
    RO_dict = {'RO': RO_pars}

    pulse_dict = {}
    pulse_dict.update(q0_pulses)
    pulse_dict.update(q1_pulses)
    pulse_dict.update(q2_pulses)
    pulse_dict.update(q3_pulses)
    pulse_dict.update(q4_pulses)
    pulse_dict.update(RO_dict)

    # N.B. Identities not needed in all cases
    pulse_combinations = [['I q0', 'I q1', 'I q2', 'I q3', 'I q4', 'RO'],
                          ['X180 q0', 'I q1', 'I q2', 'I q3', 'I q4', 'RO'],
                          ['I q0', 'X180 q1', 'I q2', 'I q3', 'I q4', 'RO'],
                          ['X180 q0', 'X180 q1', 'I q2', 'I q3', 'I q4', 'RO'],
                          ['I q0', 'I q1', 'X180 q2', 'I q3', 'I q4', 'RO'],
                          ['X180 q0', 'I q1', 'X180 q2', 'I q3', 'I q4', 'RO'],
                          ['I q0', 'X180 q1', 'X180 q2',
                              'I q3', 'I q4', 'RO'],
                          ['X180 q0', 'X180 q1', 'X180 q2',
                              'I q3', 'I q4', 'RO'],
                          ['I q0', 'I q1', 'I q2', 'X180 q3', 'I q4', 'RO'],
                          ['X180 q0', 'I q1', 'I q2', 'X180 q3', 'I q4', 'RO'],
                          ['I q0', 'X180 q1', 'I q2', 'X180 q3', 'I q4', 'RO'],
                          ['X180 q0', 'X180 q1', 'I q2',
                              'X180 q3', 'I q4', 'RO'],
                          ['I q0', 'I q1', 'X180 q2', 'X180 q3', 'I q4', 'RO'],
                          ['X180 q0', 'I q1', 'X180 q2',
                              'X180 q3', 'I q4', 'RO'],
                          ['I q0', 'X180 q1', 'X180 q2',
                              'X180 q3', 'I q4', 'RO'],
                          ['X180 q0', 'X180 q1', 'X180 q2',
                              'X180 q3', 'I q4', 'RO'],
                          ['I q0', 'I q1', 'I q2', 'I q3', 'X180 q4', 'RO'],
                          ['X180 q0', 'I q1', 'I q2', 'I q3', 'X180 q4', 'RO'],
                          ['I q0', 'X180 q1', 'I q2', 'I q3', 'X180 q4', 'RO'],
                          ['X180 q0', 'X180 q1', 'I q2',
                              'I q3', 'X180 q4', 'RO'],
                          ['I q0', 'I q1', 'X180 q2', 'I q3', 'X180 q4', 'RO'],
                          ['X180 q0', 'I q1', 'X180 q2',
                              'I q3', 'X180 q4', 'RO'],
                          ['I q0', 'X180 q1', 'X180 q2',
                              'I q3', 'X180 q4', 'RO'],
                          ['X180 q0', 'X180 q1', 'X180 q2',
                              'I q3', 'X180 q4', 'RO'],
                          ['I q0', 'I q1', 'I q2', 'X180 q3', 'X180 q4', 'RO'],
                          ['X180 q0', 'I q1', 'I q2',
                              'X180 q3', 'X180 q4', 'RO'],
                          ['I q0', 'X180 q1', 'I q2',
                              'X180 q3', 'X180 q4', 'RO'],
                          ['X180 q0', 'X180 q1', 'I q2',
                              'X180 q3', 'X180 q4', 'RO'],
                          ['I q0', 'I q1', 'X180 q2',
                              'X180 q3', 'X180 q4', 'RO'],
                          ['X180 q0', 'I q1', 'X180 q2',
                              'X180 q3', 'X180 q4', 'RO'],
                          ['I q0', 'X180 q1', 'X180 q2',
                              'X180 q3', 'X180 q4', 'RO'],
                          ['X180 q0', 'X180 q1', 'X180 q2',  'X180 q3', 'X180 q4', 'RO']]

    for i, pulse_comb in enumerate(pulse_combinations):
        pulses = []
        for p in pulse_comb:
            pulses += [pulse_dict[p]]

        el = multi_pulse_elt(i, station, pulses)
        el_list.append(el)
        seq.append_element(el, trigger_wait=True)
    station.pulsar.program_awgs(seq, *el_list, verbose=verbose)
    if return_seq:
        return seq, el_list
    else:
        return seq_name


def two_qubit_AllXY(operation_dict, q0='q0', q1='q1', RO_target='all',
                    sequence_type='simultaneous',
                    replace_q1_pulses_X180=False,
                    double_points=True,
                    verbose=False, upload=True,
                    return_seq=False):
    """
    Performs an AllXY sequence on two qubits.
    Has the option of replacing pulses on q1 with pi pulses

    Args:
        operation_dict (dict) : dictionary containing all pulse parameters
        q0, q1         (str) : target qubits for the sequence
        RO_target      (str) : target for the RO, can be a qubit name or 'all'
        sequence_type  (str) : sequential | interleaved | simultaneous | sandwiched
                              q0|q0|q1|q1   q0|q1|q0|q1   q01|q01      q1|q0|q0|q1
            describes the order of the AllXY pulses
        replace_q1_pulses_X180 (bool) : if True replaces all pulses on q1 with
            X180 pulses.

        double_points (bool) : if True measures each point in the AllXY twice
        verbose       (bool) : verbose sequence generation
        upload        (bool) :
    """
    seq_name = 'two_qubit_AllXY_{}_{}'.format(q0, q1)
    seq = sequence.Sequence(seq_name)
    station.pulsar.update_channel_settings()
    el_list = []
    sequencer_config = operation_dict['sequencer_config']

    AllXY_pulse_combinations = [['I ', 'I '], ['X180 ', 'X180 '], ['Y180 ', 'Y180 '],
                                ['X180 ', 'Y180 '], ['Y180 ', 'X180 '],
                                ['X90 ', 'I '], ['Y90 ', 'I '], [
                                    'X90 ', 'Y90 '],
                                ['Y90 ', 'X90 '], ['X90 ', 'Y180 '], [
                                    'Y90 ', 'X180 '],
                                ['X180 ', 'Y90 '], ['Y180 ', 'X90 '], [
                                    'X90 ', 'X180 '],
                                ['X180 ', 'X90 '], ['Y90 ', 'Y180 '], [
                                    'Y180 ', 'Y90 '],
                                ['X180 ', 'I '], ['Y180 ', 'I '], [
                                    'X90 ', 'X90 '],
                                ['Y90 ', 'Y90 ']]
    if double_points:
        AllXY_pulse_combinations = [val for val in AllXY_pulse_combinations
                                    for _ in (0, 1)]

    if sequence_type == 'simultaneous':
        operation_dict = deepcopy(operation_dict)  # prevents overwriting of dict
        for key in operation_dict.keys():
            if q1 in key:
                operation_dict[key]['refpoint'] = 'start'
                operation_dict[key]['pulse_delay'] = 0

    pulse_list = []
    if not replace_q1_pulses_X180:
        for pulse_comb in AllXY_pulse_combinations:
            if sequence_type == 'interleaved' or sequence_type == 'simultaneous':
                pulse_list += [[pulse_comb[0] + q0] + [pulse_comb[0] + q1] +
                               [pulse_comb[1] + q0] + [pulse_comb[1] + q1] +
                               ['RO ' + RO_target]]
            elif sequence_type == 'sequential':
                pulse_list += [[pulse_comb[0] + q0] + [pulse_comb[1] + q0] +
                               [pulse_comb[0] + q1] + [pulse_comb[1] + q1] +
                               ['RO ' + RO_target]]
            elif sequence_type == 'sandwiched':
                pulse_list += [[pulse_comb[0] + q1] + [pulse_comb[0] + q0] +
                               [pulse_comb[1] + q0] + [pulse_comb[1] + q1] +
                               ['RO ' + RO_target]]
            else:
                raise ValueError("sequence_type {} must be in".format(sequence_type) +
                                 " ['interleaved', simultaneous', 'sequential', 'sandwiched']")
    else:
        for pulse_comb in AllXY_pulse_combinations:
            if sequence_type == 'interleaved' or sequence_type == 'simultaneous':
                pulse_list += [[pulse_comb[0] + q0] + ['X180 ' + q1] +
                               [pulse_comb[1] + q0] + ['X180 ' + q1] +
                               ['RO ' + RO_target]]
            elif sequence_type == 'sequential':
                pulse_list += [[pulse_comb[0] + q0] + [pulse_comb[1] + q0] +
                               ['X180 ' + q1] + ['X180 ' + q1] +
                               ['RO ' + RO_target]]
            elif sequence_type == 'sandwiched':
                pulse_list += [['X180 ' + q1] + [pulse_comb[0] + q0] +
                               [pulse_comb[1] + q0] + ['X180 ' + q1] +
                               ['RO ' + RO_target]]
            else:
                raise ValueError("sequence_type {} must be in".format(sequence_type) +
                                 " ['interleaved', simultaneous', 'sequential', 'sandwiched']")

    for i, pulse_comb in enumerate(pulse_list):
        pulses = []
        for p in pulse_comb:
            pulses += [operation_dict[p]]

        el = multi_pulse_elt(i, station, pulses, sequencer_config)
        el_list.append(el)
        seq.append_element(el, trigger_wait=True)
    if upload:
        station.pulsar.program_awgs(seq, *el_list, verbose=verbose)
    if return_seq:
        return seq, el_list
    else:
        return seq_name


def two_qubit_tomo_cardinal(cardinal,
                            q0_pulse_pars,
                            q1_pulse_pars,
                            RO_pars,
                            timings_dict,
                            verbose=False,
                            upload=True,
                            return_seq=False):

    seq_name = '2_qubit_Card_%d_seq' % cardinal
    seq = sequence.Sequence(seq_name)
    station.pulsar.update_channel_settings()
    el_list = []
    # Create a dict with the parameters for all the pulses
    q0_pulses = add_suffix_to_dict_keys(
        get_pulse_dict_from_pars(q0_pulse_pars), ' q0')
    q1_pulses = add_suffix_to_dict_keys(
        get_pulse_dict_from_pars(q1_pulse_pars), ' q1')
    RO_dict = {'RO': RO_pars}

    pulse_dict = {}
    pulse_dict.update(q0_pulses)
    pulse_dict.update(q1_pulses)
    pulse_dict.update(RO_dict)

    # Timings
    # FIXME: This dictionary should not be required? -MAR
    # NOTE: required in the CPhase tomo as input but not used
    QQ_buffer = timings_dict['QQ_buffer']
    wait_time = timings_dict['wait_time']
    msmt_buffer = timings_dict['msmt_buffer']

    tomo_list_q0 = ['I q0', 'X180 q0', 'Y90 q0',
                    'mY90 q0', 'X90 q0', 'mX90 q0']
    tomo_list_q1 = ['I q1', 'X180 q1', 'Y90 q1',
                    'mY90 q1', 'X90 q1', 'mX90 q1']

    # inner loop on q0
    prep_idx_q0 = int(cardinal % 6)
    prep_idx_q1 = int(((cardinal - prep_idx_q0)/6) % 6)

    prep_pulse_q0 = pulse_dict[tomo_list_q0[prep_idx_q0]]
    prep_pulse_q1 = pulse_dict[tomo_list_q1[prep_idx_q1]]

    prep_pulse_q1['pulse_delay'] = QQ_buffer + (prep_pulse_q0['sigma'] *
                                                prep_pulse_q0['nr_sigma'])

    RO_pars['pulse_delay'] += msmt_buffer - (prep_pulse_q1['sigma'] *
                                             prep_pulse_q1['nr_sigma'])

    # Calibration points
    cal_points = [['I q0', 'I q1', 'RO'],
                  ['I q0', 'I q1', 'RO'],
                  ['I q0', 'I q1', 'RO'],
                  ['I q0', 'I q1', 'RO'],
                  ['I q0', 'I q1', 'RO'],
                  ['I q0', 'I q1', 'RO'],
                  ['I q0', 'I q1', 'RO'],
                  ['X180 q0', 'I q1', 'RO'],
                  ['X180 q0', 'I q1', 'RO'],
                  ['X180 q0', 'I q1', 'RO'],
                  ['X180 q0', 'I q1', 'RO'],
                  ['X180 q0', 'I q1', 'RO'],
                  ['X180 q0', 'I q1', 'RO'],
                  ['X180 q0', 'I q1', 'RO'],
                  ['I q0', 'X180 q1', 'RO'],
                  ['I q0', 'X180 q1', 'RO'],
                  ['I q0', 'X180 q1', 'RO'],
                  ['I q0', 'X180 q1', 'RO'],
                  ['I q0', 'X180 q1', 'RO'],
                  ['I q0', 'X180 q1', 'RO'],
                  ['I q0', 'X180 q1', 'RO'],
                  ['X180 q0', 'X180 q1', 'RO'],
                  ['X180 q0', 'X180 q1', 'RO'],
                  ['X180 q0', 'X180 q1', 'RO'],
                  ['X180 q0', 'X180 q1', 'RO'],
                  ['X180 q0', 'X180 q1', 'RO'],
                  ['X180 q0', 'X180 q1', 'RO'],
                  ['X180 q0', 'X180 q1', 'RO']]

    for i in range(36):
        tomo_idx_q0 = int(i % 6)
        tomo_idx_q1 = int(((i - tomo_idx_q0)/6) % 6)

        # print(i,tomo_idx_q0,tomo_idx_q1)

        tomo_pulse_q0 = pulse_dict[tomo_list_q0[tomo_idx_q0]]
        tomo_pulse_q1 = pulse_dict[tomo_list_q1[tomo_idx_q1]]

        tomo_pulse_q0['pulse_delay'] = wait_time + (prep_pulse_q1['sigma'] *
                                                    prep_pulse_q1['nr_sigma'])

        tomo_pulse_q1['pulse_delay'] = QQ_buffer + (tomo_pulse_q0['sigma'] *
                                                    tomo_pulse_q0['nr_sigma'])
        pulse_list = [prep_pulse_q0,
                      prep_pulse_q1,
                      tomo_pulse_q0,
                      tomo_pulse_q1,
                      RO_pars]
        el = multi_pulse_elt(i, station, pulse_list)
        el_list.append(el)
        seq.append_element(el, trigger_wait=True)

    for i, pulse_comb in enumerate(cal_points):
        pulses = []
        for p in pulse_comb:
            pulses += [pulse_dict[p]]

        el = multi_pulse_elt(35+i, station, pulses)
        el_list.append(el)
        seq.append_element(el, trigger_wait=True)

    station.pulsar.program_awgs(seq, *el_list, verbose=verbose)
    if return_seq:
        return seq, el_list
    else:
        return seq_name


def two_qubit_tomo_bell(bell_state,
                        operation_dict,
                        qS,
                        qCZ,
                        RO_target,
                        distortion_dict,
                        CZ_disabled=False,
                        cal_points_with_flux_pulses=True,
                        verbose=False,
                        upload=True):
    '''
        qS is swap qubit
        qCZ is cphase qubit
    '''
    sequencer_config = operation_dict['sequencer_config']

    seq_name = '2_qubit_Bell_Tomo_%d_seq' % bell_state
    seq = sequence.Sequence(seq_name)
    station.pulsar.update_channel_settings()
    el_list = []
    tomo_list_qS = []
    tomo_list_qCZ = []
    # Tomo pulses span a basis covering all the cardinal points
    tomo_pulses = ['I ', 'X180 ', 'Y90 ', 'mY90 ', 'X90 ', 'mX90 ']
    for tp in tomo_pulses:
        tomo_list_qS += [tp+qS]
        tomo_list_qCZ += [tp+qCZ]

    ###########################
    # Defining sub sequences #
    ###########################
    # This forms the base sequence, note that gate1, gate2 and after_pulse will
    # be replaced to prepare the desired state and tomo1 and tomo2 will be
    # replaced with tomography pulses
    base_sequence = (
        ['gate1 ' + qS, 'gate2 ' + qCZ,
         'SWAP '+qS, 'CZ ' + qCZ, 'rSWAP ' + qS,
         'SWAP_corr ' + qS, 'CZ_corr ' + qCZ,
         'after_pulse ' + qCZ, 'tomo1 '+qCZ, 'tomo2 '+qS, 'RO '+RO_target])

    # Calibration points
    # every calibration point is repeated 7 times to have 64 elts in totalb
    cal_points = [['I '+qCZ, 'I '+qS, 'RO '+RO_target]]*7 +\
                  [['I '+qCZ, 'X180 '+qS, 'RO '+RO_target]]*7 +\
                  [['X180 '+qCZ, 'I '+qS, 'RO '+RO_target]]*7 +\
                  [['X180 '+qCZ, 'X180 '+qS, 'RO '+RO_target]]*7

    if CZ_disabled:
        operation_dict['CZ '+qCZ]['amplitude'] = 0
        operation_dict['CZ '+qCZ]['phase_corr_pulse_amp'] = 0

    ################################################
    # Creating additional pulses for this sequence #
    ################################################
    # the recovery SWAP is identical to the regular SWAP operation, unless
    # an rSWAP is explicitly contained in the operation dict
    if ('rSWAP ' + qS) not in operation_dict.keys():
        operation_dict['rSWAP ' + qS] = deepcopy(operation_dict['SWAP ' + qS])
    operation_dict['CZ_corr ' + qCZ]['refpoint'] = 'simultaneous'

    ################
    # Bell states  #
    ################
    if bell_state == 0:  # |Phi_m>=|00>-|11>
        gate1 = 'Y90 ' + qS
        gate2 = 'Y90 ' + qCZ
        after_pulse = 'mY90 ' + qCZ
    elif bell_state == 1:  # |Phi_p>=|00>+|11>
        gate1 = 'mY90 ' + qS
        gate2 = 'Y90 ' + qCZ
        after_pulse = 'mY90 ' + qCZ
    elif bell_state == 2:  # |Psi_m>=|01> - |10>
        gate1 = 'Y90 ' + qS
        gate2 = 'mY90 ' + qCZ
        after_pulse = 'mY90 ' + qCZ
    elif bell_state == 3:  # |Psi_p>=|01> + |10>
        gate1 = 'mY90 ' + qS
        gate2 = 'mY90 ' + qCZ
        after_pulse = 'mY90 ' + qCZ

    # Below are states with the initial pulse on the CP-qubit disabled
    # these are not Bell states but are used for debugging
    elif bell_state == 0+10:  # |00>+|11>
        gate1 = 'Y90 ' + qS
        gate2 = 'I ' + qCZ
        after_pulse = 'mY90 ' + qCZ
    elif bell_state == 1+10:
        gate1 = 'mY90 ' + qS
        gate2 = 'I ' + qCZ
        after_pulse = 'mY90 ' + qCZ
    elif bell_state == 2+10:  # |01> - |10>
        gate1 = 'Y90 ' + qS
        gate2 = 'I ' + qCZ
        after_pulse = 'mY90 ' + qCZ
    elif bell_state == 3+10:
        gate1 = 'mY90 ' + qS
        gate2 = 'I ' + qCZ
        after_pulse = 'mY90 ' + qCZ

    # Below are states with the initial pulse on the SWAP-qubit disabled
    # these are not Bell states but are used for debugging
    elif bell_state == 0 + 20:  # |00>+|11>
        gate1 = 'I ' + qS
        gate2 = 'Y90 ' + qCZ
        after_pulse = 'mY90 ' + qCZ
    elif bell_state == 1 + 20:  # |01> - |10>
        gate1 = 'I ' + qS
        gate2 = 'Y90 ' + qCZ
        after_pulse = 'mY90 ' + qCZ
    elif bell_state == 2 + 20:
        gate1 = 'I ' + qS
        gate2 = 'mY90 ' + qCZ
        after_pulse = 'mY90 ' + qCZ
    elif bell_state == 3 + 20:
        gate1 = 'mY90 ' + qS
        gate2 = 'mY90 ' + qCZ
        after_pulse = 'mY90 ' + qCZ

    print('Compensation qCP {:.3f}'.format(
        operation_dict['CZ_corr ' + qCZ]['amplitude']))
    print('Compensation qS {:.3f}'.format(
        operation_dict['SWAP_corr ' + qS]['amplitude']))

    ########################################################
    #  Here the actual pulses of all elements get defined  #
    ########################################################
    # We start by replacing the state prepartion pulses
    base_sequence[0] = gate1
    base_sequence[1] = gate2
    base_sequence[7] = after_pulse

    seq_pulse_list = []

    for i in range(36):
        tomo_idx_qS = int(i % 6)
        tomo_idx_qCZ = int(((i - tomo_idx_qS)/6) % 6)
        base_sequence[8] = tomo_list_qCZ[tomo_idx_qCZ]
        base_sequence[9] = tomo_list_qS[tomo_idx_qS]
        seq_pulse_list += [deepcopy(base_sequence)]
    print(len(cal_points))
    for cal_pulses in cal_points:
        if cal_points_with_flux_pulses:
            base_sequence[0] = 'I ' + qS
            base_sequence[1] = 'I ' + qCZ
            base_sequence[7] = 'I ' + qCZ
            base_sequence[-3:] = cal_pulses
            seq_pulse_list += [deepcopy(base_sequence)]
        else:
            seq_pulse_list += [cal_pulses]

    for i, pulse_list in enumerate(seq_pulse_list):
        pulses = []
        for p in pulse_list:
            pulses += [operation_dict[p]]
        el = multi_pulse_elt(i, station, pulses, sequencer_config)
        if distortion_dict is not None:
            print('\rDistorting element {}/{} '.format(i+1,
                                                       len(seq_pulse_list)),
                  end='')
            el = distort_and_compensate(
                el, distortion_dict)
        el_list.append(el)
        seq.append_element(el, trigger_wait=True)

    station.pulsar.program_awgs(seq, *el_list, verbose=verbose)

    return seq, el_list


def cphase_fringes(phases, q0_pulse_pars, q1_pulse_pars, RO_pars,
                   swap_pars_q0, cphase_pars_q1, timings_dict,
                   distortion_dict, verbose=False, upload=True, return_seq=False):
    '''
    '''
    preloaded_kernels_vec = preload_kernels_func(distortion_dict)
    original_delay = deepcopy(RO_pars)[0]['pulse_delay']
    seq_name = 'CPhase'
    seq = sequence.Sequence(seq_name)
    station.pulsar.update_channel_settings()
    el_list = []
    # print(q0_pulse_pars)
    q0_pulses = add_suffix_to_dict_keys(
        get_pulse_dict_from_pars(q0_pulse_pars[0]), ' q0')
    q1_pulses = add_suffix_to_dict_keys(
        get_pulse_dict_from_pars(q1_pulse_pars[0]), ' q1')

    pulse_dict = {}
    pulse_dict.update(q0_pulses)
    pulse_dict.update(q1_pulses)
    pulse_dict.update({'RO': RO_pars[0]})
    # print({'RO': RO_pars})

    # Timings
    buffer_mw_flux = timings_dict[0]['buffer_mw_flux']
    buffer_flux_mw = timings_dict[0]['buffer_flux_mw']
    msmt_buffer = timings_dict[0]['msmt_buffer']
    dead_time = timings_dict[0]['dead_time']
    # print(buffer_mw_flux,buffer_flux_mw,msmt_buffer,dead_time)

    # defining main pulses
    exc_pulse = deepcopy(pulse_dict['X180 q0'])
    exc_pulse['pulse_delay'] += 0.01e-6
    swap_pulse_1 = deepcopy(swap_pars_q0[0])
    # print(swap_pulse_1)
    swap_pulse_1['pulse_delay'] = buffer_mw_flux + \
        exc_pulse['sigma']*exc_pulse['nr_sigma']

    ramsey_1 = deepcopy(pulse_dict['Y90 q1'])
    ramsey_1['pulse_delay'] = buffer_flux_mw + swap_pulse_1['length']
    cphase_pulse = cphase_pars_q1[0]
    cphase_amp = cphase_pulse['amplitude']
    cphase_pulse['pulse_delay'] = buffer_mw_flux + \
        ramsey_1['sigma']*ramsey_1['nr_sigma']
    ramsey_2 = deepcopy(pulse_dict['X90 q1'])
    ramsey_2['pulse_delay'] = buffer_flux_mw + cphase_pulse['length']

    swap_pulse_2 = deepcopy(swap_pars_q0[0])
    swap_pulse_2['pulse_delay'] = buffer_mw_flux + \
        ramsey_2['sigma']*ramsey_2['nr_sigma']
    RO_pars[0]['pulse_delay'] = msmt_buffer + swap_pulse_2['length']

    # defining compensation pulses
    swap_comp_1 = deepcopy(swap_pulse_1)
    swap_pulse_1['pulse_delay'] = RO_pars[0]['length'] + dead_time
    cphase_comp = deepcopy(cphase_pulse)
    swap_comp_2 = deepcopy(swap_pulse_2)

    dead_time_pulse = {'pulse_type': 'SquarePulse',
                       'pulse_delay': RO_pars[0]['pulse_delay'],
                       'channel': swap_pars_q0[0]['channel'],
                       'amplitude': 0,
                       'length': dead_time}

    for i, ph2 in enumerate(phases[0]):
        # print(ph2)
        ramsey_2['phase'] = ph2

        cphase_pulse['amplitude'] = cphase_amp
        pulse_list = [exc_pulse,
                      swap_pulse_1,
                      ramsey_1,
                      cphase_pulse,
                      ramsey_2,
                      swap_pulse_2,
                      RO_pars[0],
                      swap_comp_1,
                      cphase_comp,
                      swap_comp_2,
                      dead_time_pulse]
        el = multi_pulse_elt(2*i, station, pulse_list)
        el_list.append(el)

        cphase_pulse['amplitude'] = 0.
        pulse_list = [exc_pulse,
                      swap_pulse_1,
                      ramsey_1,
                      cphase_pulse,
                      ramsey_2,
                      swap_pulse_2,
                      RO_pars[0],
                      swap_comp_1,
                      cphase_comp,
                      swap_comp_2,
                      dead_time_pulse]
        el = multi_pulse_elt(2*i+1, station, pulse_list)
        el_list.append(el)

    # Compensations
    for i, el in enumerate(el_list):
        if distortion_dict is not None:
            el = distort_and_compensate(
                el, distortion_dict, preloaded_kernels_vec)
            el_list[i] = el
        seq.append_element(el, trigger_wait=True)
    cal_points = 4
    RO_pars[0]['pulse_delay'] = original_delay

    # Calibration points
    cal_points = [['I q0', 'I q1', 'RO'],
                  ['I q0', 'I q1', 'RO'],
                  ['X180 q0', 'I q1', 'RO'],
                  ['X180 q0', 'I q1', 'RO'],
                  ['I q0', 'X180 q1', 'RO'],
                  ['I q0', 'X180 q1', 'RO'],
                  ['X180 q0', 'X180 q1', 'RO'],
                  ['X180 q0', 'X180 q1', 'RO']]

    for i, pulse_comb in enumerate(cal_points):
        pulses = []
        for p in pulse_comb:
            pulses += [pulse_dict[p]]
        pulses[0]['pulse_delay'] += 0.01e-6

        el = multi_pulse_elt(2*len(phases)+i, station, pulses)
        el_list.append(el)
        seq.append_element(el, trigger_wait=True)

    # upload
    if upload:
        station.pulsar.program_awgs(seq, *el_list, verbose=verbose)
    if return_seq:
        return seq, el_list
    else:
        return seq


def preload_kernels_func(distortion_dict):
    output_dict = {ch: [] for ch in distortion_dict['ch_list']}
    for ch in distortion_dict['ch_list']:
        for kernel in distortion_dict[ch]:
            if kernel is not '':
                if kernel in cached_kernels.keys():
                    print('Cached {}'.format(kernel_dir+kernel))
                    output_dict[ch].append(cached_kernels[kernel])
                else:
                    print('Loading {}'.format(kernel_dir+kernel))
                    # print(os.path.isfile('kernels/'+kernel))
                    kernel_vec = np.loadtxt(kernel_dir+kernel)
                    output_dict[ch].append(kernel_vec)
                    cached_kernels.update({kernel: kernel_vec})
    return output_dict

def two_qubit_tomo_cphase_cardinal(cardinal_state,
                        operation_dict,
                        qS,
                        qCZ,
                        RO_target,
                        distortion_dict,
                        CZ_disabled=False,
                        cal_points_with_flux_pulses=True,
                        verbose=False,
                        upload=True):
    '''
        qS is swap qubit
        qCZ is cphase qubit
    '''
    sequencer_config = operation_dict['sequencer_config']

    seq_name = '2_qubit_CPhase_Cardinal_Tomo_%d_seq' % cardinal_state
    seq = sequence.Sequence(seq_name)
    station.pulsar.update_channel_settings()
    el_list = []
    tomo_list_qS = []
    tomo_list_qCZ = []
    # Tomo pulses span a basis covering all the cardinal points
    tomo_pulses = ['I ', 'X180 ', 'Y90 ', 'mY90 ', 'X90 ', 'mX90 ']
    for tp in tomo_pulses:
        tomo_list_qS += [tp+qS]
        tomo_list_qCZ += [tp+qCZ]

    ###########################
    # Defining sub sequences #
    ###########################
    # This forms the base sequence, note that gate1, gate2 and after_pulse will
    # be replaced to prepare the desired state and tomo1 and tomo2 will be
    # replaced with tomography pulses
    base_sequence = (
        ['gate1 ' + qS, 'gate2 ' + qCZ,
         'SWAP '+qS, 'CZ ' + qCZ, 'rSWAP ' + qS,
         'SWAP_corr ' + qS, 'CZ_corr ' + qCZ,
         'after_pulse ' + qCZ, 'tomo1 '+qCZ, 'tomo2 '+qS, 'RO '+RO_target])

    # Calibration points
    # every calibration point is repeated 7 times to have 64 elts in total
    cal_points = [['I '+qCZ, 'I '+qS, 'RO '+RO_target]]*7 +\
                  [['I '+qCZ, 'X180 '+qS, 'RO '+RO_target]]*7 +\
                  [['X180 '+qCZ, 'I '+qS, 'RO '+RO_target]]*7 +\
                  [['X180 '+qCZ, 'X180 '+qS, 'RO '+RO_target]]*7

    if CZ_disabled:
        operation_dict['CZ '+qCZ]['amplitude'] = 0
        operation_dict['CZ '+qCZ]['phase_corr_pulse_amp'] = 0

    ################################################
    # Creating additional pulses for this sequence #
    ################################################
    # the recovery SWAP is identical to the regular SWAP operation, unless
    # an rSWAP is explicitly contained in the operation dict
    if ('rSWAP ' + qS) not in operation_dict.keys():
        operation_dict['rSWAP ' + qS] = deepcopy(operation_dict['SWAP ' + qS])
    operation_dict['CZ_corr ' + qCZ]['refpoint'] = 'simultaneous'

    ################
    # cardinal states  #
    ################
    # here select the qubit gates (depending on cardinal_state)
    prep_idx_qS = int(cardinal_state % 6)
    prep_idx_qCZ = int(((cardinal_state - prep_idx_qS)/6) % 6)

    print('Compensation qCP {:.3f}'.format(
        operation_dict['CZ_corr ' + qCZ]['amplitude']))
    print('Compensation qS {:.3f}'.format(
        operation_dict['SWAP_corr ' + qS]['amplitude']))

    ########################################################
    #  Here the actual pulses of all elements get defined  #
    ########################################################
    # We start by replacing the state prepartion pulses
    base_sequence[0] = tomo_list_qS[prep_idx_qS]
    base_sequence[1] = tomo_list_qCZ[prep_idx_qCZ]
    base_sequence[7] = 'I ' + qCZ

    seq_pulse_list = []

    for i in range(36):
        tomo_idx_qS = int(i % 6)
        tomo_idx_qCZ = int(((i - tomo_idx_qS)/6) % 6)
        base_sequence[8] = tomo_list_qCZ[tomo_idx_qCZ]
        base_sequence[9] = tomo_list_qS[tomo_idx_qS]
        seq_pulse_list += [deepcopy(base_sequence)]
    print(len(cal_points))
    for cal_pulses in cal_points:
        if cal_points_with_flux_pulses:
            base_sequence[0] = 'I ' + qS
            base_sequence[1] = 'I ' + qCZ
            base_sequence[7] = 'I ' + qCZ
            base_sequence[-3:] = cal_pulses
            seq_pulse_list += [deepcopy(base_sequence)]
        else:
            seq_pulse_list += [cal_pulses]

    for i, pulse_list in enumerate(seq_pulse_list):
        pulses = []
        for p in pulse_list:
            pulses += [operation_dict[p]]
        el = multi_pulse_elt(i, station, pulses, sequencer_config)
        if distortion_dict is not None:
            print('\rDistorting element {}/{} '.format(i+1,
                                                       len(seq_pulse_list)),
                  end='')
            el = distort_and_compensate(
                el, distortion_dict)
        el_list.append(el)
        seq.append_element(el, trigger_wait=True)

    station.pulsar.program_awgs(seq, *el_list, verbose=verbose)

    return seq, el_list


def n_qubit_off_on(pulse_pars_list, RO_pars, return_seq=False, verbose=False,
                   parallel_pulses=False, preselection=False, upload=True,
                   RO_spacing=200e-9):
    n = len(pulse_pars_list)
    seq_name = '{}_qubit_OffOn_sequence'.format(n)
    seq = sequence.Sequence(seq_name)
    el_list = []

    # Create a dict with the parameters for all the pulses
    pulse_dict = {'RO': RO_pars}
    for i, pulse_pars in enumerate(pulse_pars_list):
        pars = pulse_pars.copy()
        if i != 0 and parallel_pulses:
            pars['refpoint'] = 'simultaneous'
        pulses = add_suffix_to_dict_keys(
            get_pulse_dict_from_pars(pars), ' {}'.format(i))
        pulse_dict.update(pulses)
    spacerpulse = {'pulse_type': 'SquarePulse',
                   'channel': RO_pars['acq_marker_channel'],
                   'amplitude': 0.0,
                   'length': RO_spacing,
                   'pulse_delay': 0}
    pulse_dict.update({'spacer': spacerpulse})

    # Create a list of required pulses
    pulse_combinations = []
    for pulse_list in itertools.product(*(n*[['I', 'X180']])):
        pulse_comb = (n+1)*['']
        for i, pulse in enumerate(pulse_list):
            pulse_comb[i] = pulse + ' {}'.format(i)
        pulse_comb[-1] = 'RO'
        if preselection:
            pulse_comb = ['RO', 'spacer'] + pulse_comb
        pulse_combinations.append(pulse_comb)

    for i, pulse_comb in enumerate(pulse_combinations):
        pulses = []
        for j, p in enumerate(pulse_comb):
            pulses += [pulse_dict[p]]
        el = multi_pulse_elt(i, station, pulses)
        el_list.append(el)
        seq.append_element(el, trigger_wait=True)
    if upload:
        station.pulsar.program_awgs(seq, *el_list, verbose=verbose)
    if return_seq:
        return seq, el_list
    else:
        return seq_name


def n_qubit_simultaneous_randomized_benchmarking_seq(pulse_pars_list, RO_pars,
                                                     nr_cliffords_value, #scalar
                                                     nr_seeds,           #array
                                                     idx_for_RB=0,
                                                     return_seq=False,
                                                     CxC_RB=True,
                                                     net_clifford=0,
                                                     gate_decomposition='HZ',
                                                     interleaved_gate=None,
                                                     post_msmt_delay=3e-6,
                                                     seq_name=None,
                                                     verbose=False):

    # Here RO_pars must contain the RO pulse for multiplexed RO on the
    # relevant qubits.
    # idx_for_RB refers to the index of the pulse_pars in pulse_pars_list
    # which will undergo the RB protocol in the case CxC_RB==False (i.e. the
    # position of the Z operator when we measure ZIII..I, IZII..I, IIZI..I etc.

    # get number of qubits
    n = len(pulse_pars_list)

    # Create a dict with the parameters for all the pulses
    pulse_dict = {'RO': RO_pars}
    for i, pulse_pars in enumerate(pulse_pars_list):
        pars = pulse_pars.copy()
        if i != 0:
            pars['refpoint'] = 'start'

        pulse_dict_qb = deepcopy(get_pulse_dict_from_pars(pars))
        Z0 = deepcopy(pulse_dict_qb['Z180'])
        Z0['phase'] = 0
        pulse_dict_qb.update({'Z0': Z0})
        pulses = add_suffix_to_dict_keys(pulse_dict_qb, ' {}'.format(i))
        pulse_dict.update(pulses)

    if CxC_RB:
        if seq_name is None:
            seq_name = 'CxC_RB_sequence'
        seq = sequence.Sequence(seq_name)
        el_list = []

        for i in nr_seeds:
            clifford_sequence_list = []
            for index in range(n):
                clifford_sequence_list.append(rb.randomized_benchmarking_sequence(
                    nr_cliffords_value, desired_net_cl=net_clifford,
                    interleaved_gate=interleaved_gate))

            pulse_keys = rb.decompose_clifford_seq_n_qubits(
                clifford_sequence_list,
                gate_decomp=gate_decomposition)

            # interleave pulses for each qubit to obtain [pulse0_qb0,
            # pulse0_qb1,...pulse0_qbN,...,pulseN_qb0, pulseN_qb1,...,pulseN_qbN]
            pulse_keys_w_suffix = []
            for k, lst in enumerate(pulse_keys):
                pulse_keys_w_suffix.append([x+' '+str(k % n) for x in lst])
            pulse_keys_by_qubit = []
            for k in range(n):
                pulse_keys_by_qubit.append([x for l in pulse_keys_w_suffix[k::n]
                                            for x in l])

            pulse_list = []
            for j in range(len(pulse_keys_by_qubit[0])):
                for k in range(n):
                    pulse_list.append(pulse_dict[pulse_keys_by_qubit[k][j]])

            # if qb0 has a Z_pulse, remove the 'refpoint' key in the pulse pars
            # dict of the next qubit which has an SSB pulse
            Zp0_idxs = [] # indices of the Z pulses on qb0
            for w, px in enumerate(pulse_list):
                if (px['target_qubit']==pulse_pars_list[0]['target_qubit'] and
                            px['pulse_type']=='Z_pulse'):
                    Zp0_idxs.append(w)
            if len(Zp0_idxs)>0:
                for y in Zp0_idxs:
                    #look at the pulses applied on qb1...qbn
                    qubit_length_pulse_list = pulse_list[y+1:y+n]
                    # for each pulse in pulse_list where qb0 has a Z pulse,
                    # look at the n-1 entries (qubits) and save the indices
                    # of all SSB pulse parameters
                    SSB_after_Z_on_qb0 = [y+1+qubit_length_pulse_list.index(j)
                                          for j in qubit_length_pulse_list
                                          if j['pulse_type']!='Z_pulse']
                    if len(SSB_after_Z_on_qb0)>0:
                        # if SSB pulses were found, delete the 'refpoint' entry
                        # in the first qb after qb0 that has an SSB pulse
                        first_SSB = next(y+1+qubit_length_pulse_list.index(j)
                                         for j in qubit_length_pulse_list
                                         if j['pulse_type']!='Z_pulse')
                        temp_SSB_pulse = deepcopy(pulse_list[first_SSB])
                        temp_SSB_pulse.pop('refpoint')
                        pulse_list[first_SSB] = temp_SSB_pulse

            # add RO pulse pars at the end
            pulse_list += [RO_pars]

            # find index of first pulse in pulse_list that is not a Z pulse
            # copy this pulse and set extra wait
            try:
                first_x_pulse = next(j for j in pulse_list
                                     if 'Z' not in j['pulse_type'])
                first_x_pulse_idx = pulse_list.index(first_x_pulse)
            except:
                first_x_pulse_idx = 0
            pulse_list[first_x_pulse_idx] = deepcopy(pulse_list[first_x_pulse_idx])
            pulse_list[first_x_pulse_idx]['pulse_delay'] += post_msmt_delay

            if verbose:
                print('pulse_keys_by_qubit ', pulse_keys_by_qubit)
                # print('\nfinal pulse_list ', pulse_list)
                print('\nlen_pulse_list/nr_qubits ',(len(pulse_list)-1)/n)
                print('\nnr_finite_duration_pulses/nr_qubits ',
                      len([x for x in pulse_list[:-1]
                           if 'Z' not in x['pulse_type']])/n)
                print('\nnr_Z_pulses/nr_qubits ', len([x for x in pulse_list
                                                       if 'Z' in x['pulse_type']])/n)
                print('\n i ', i)
            el = multi_pulse_elt(i, station, pulse_list)
            el_list.append(el)
            seq.append_element(el, trigger_wait=True)

    else:

        if idx_for_RB > n-1:
            raise ValueError('idx_for_RB cannot exceed (nr_of_qubits-1).')

        if seq_name is None:
            seq_name = 'CxI_IxC_RB_sequence'
        seq = sequence.Sequence(seq_name)
        el_list = []

        for i in nr_seeds:
            cl_seq = rb.randomized_benchmarking_sequence(
                nr_cliffords_value, desired_net_cl=net_clifford,
                interleaved_gate=interleaved_gate)
            pulse_keys = rb.decompose_clifford_seq(
                cl_seq,
                gate_decomp=gate_decomposition)

            C_pulse_list_keys = [x+' '+str(idx_for_RB) for x in pulse_keys]
            pulse_list_keys = len(C_pulse_list_keys)*n*['']
            pulse_list_keys[idx_for_RB::n] = C_pulse_list_keys

            # populate remaining positions in pulse_list with I pulses if
            # the pulse from RB is a finite-duration pulse, or with Z0 if the
            # pulse from RB is a Z puls
            for index in range(0,int(len(pulse_list_keys)),n):
                for j, key in enumerate(pulse_list_keys[index:index+n]):
                    if key=='':
                        if 'Z' in pulse_list_keys[index:index+n][idx_for_RB]:
                            pulse_list_keys[index+j] = 'Z0 '+ str(j)
                        else:
                            pulse_list_keys[index+j] = 'I '+ str(j)

            # create pulse list to upload
            pulse_list = [pulse_dict[x] for x in pulse_list_keys]

            # if qb0 has a Z_pulse, remove the 'refpoint' key of the next
            # pulse dict which is not a Z_pulse
            Zp0_idxs = [] # indices of the Z pulses on qb0
            for w, px in enumerate(pulse_list):
                if (px['target_qubit']==pulse_pars_list[0]['target_qubit']
                        and px['pulse_type']=='Z_pulse'):
                    Zp0_idxs.append(w)
            if len(Zp0_idxs)>0:
                for y in Zp0_idxs:
                    #look at the pulses applied on qb1...qbn
                    qubit_length_pulse_list = pulse_list[y+1:y+n]
                    # for each pulse in pulse_list where qb0 has a Z pulse,
                    # look at the n-1 entries (qubits) and save the indices
                    # of all SSB pulse parameters
                    SSB_after_Z_on_qb0 = [y+1+qubit_length_pulse_list.index(j)
                                          for j in qubit_length_pulse_list
                                          if j['pulse_type']!='Z_pulse']
                    if len(SSB_after_Z_on_qb0)>0:
                        # if SSB pulses were found, delete the 'refpoint' entry
                        # in the first qb after qb0 that has an SSB pulse
                        first_SSB = next(y+1+qubit_length_pulse_list.index(j)
                                         for j in qubit_length_pulse_list
                                         if j['pulse_type']!='Z_pulse')
                        temp_SSB_pulse = deepcopy(pulse_list[first_SSB])
                        temp_SSB_pulse.pop('refpoint')
                        pulse_list[first_SSB] = temp_SSB_pulse

            # add RO pars
            pulse_list += [RO_pars]

            # find first_x_pulse = first pulse in pulse_list that is not a Z pulse
            # Copy this pulse and the next first_x_pulse_idx*n-first_x_pulse_idx,
            # and set extra wait
            try:
                first_x_pulse = next(j for j in pulse_list
                                     if 'Z' not in j['pulse_type'])
                first_x_pulse_idx = pulse_list.index(first_x_pulse)
            except:
                first_x_pulse_idx = 0
            pulse_list[first_x_pulse_idx] = deepcopy(pulse_list[first_x_pulse_idx])
            pulse_list[first_x_pulse_idx]['pulse_delay'] += post_msmt_delay

            if verbose:
                print('pulse_list_keys ', pulse_list_keys)
                # print('\nfinal pulse_list ', pulse_list)
                print('\nlen_pulse_list/nr_qubits ',(len(pulse_list)-1)/n)
                print('\nnr_finite_duration_pulses/nr_qubits ',
                      len([x for x in pulse_list[:-1]
                           if 'Z' not in x['pulse_type']])/n)
                print('\nnr_Z_pulses/nr_qubits ', len([x for x in pulse_list
                                                       if 'Z' in x['pulse_type']])/n)
                print('\n i ', i)
            el = multi_pulse_elt(i, station, pulse_list)
            el_list.append(el)
            seq.append_element(el, trigger_wait=True)

    station.pulsar.program_awgs(seq, *el_list, verbose=verbose)
    if return_seq:
        return seq, el_list
    else:
        return seq_name



def two_qubit_tomo_bell_qudev(bell_state,
                              qb_c,
                              qb_t,
                              # RO_target,
                              RO_pars,
                              num_flux_pulses=0,
                              distortion_dict=None,
                              CZ_disabled=False,
                              cal_points_with_flux_pulses=True,
                              verbose=False,
                              # station=None,
                              upload=True
                              ):
    '''
        qb_c is the control qubit (pulsed)
        qb_t is the target qubit
    '''


    if station is None:
        logging.warning('No station specified.')

    qCZ = qb_c.name
    qS = qb_t.name

    sequencer_config = station.sequencer_config
    operation_dict = qb_c.get_operation_dict()
    operation_dict.update(qb_t.get_operation_dict())


    seq_name = '2_qubit_Bell_Tomo_%d_seq' % bell_state
    seq = sequence.Sequence(seq_name)
    el_list = []
    tomo_list_qS = []
    tomo_list_qCZ = []
    # Tomo pulses span a basis covering all the cardinal points
    # tomo_pulses = ['I ', 'X180 ', 'X90 ', 'Y90 ', 'mX90 ', 'mY90 ']
    tomo_pulses = ['I ', 'X180 ', 'Y90 ', 'mY90 ', 'X90 ', 'mX90 ']
    for tp in tomo_pulses:
        tomo_list_qS += [tp+qS]
        tomo_list_qCZ += [tp+qCZ]

    ###########################
    # Defining sub sequences #
    ###########################
    # This forms the base sequence, note that gate1, gate2 and after_pulse will
    # be replaced to prepare the desired state and tomo1 and tomo2 will be
    # replaced with tomography pulses
    base_sequence = ['gate1 ' + qS, 'gate2 ' + qCZ, 'CZ_corr ' + qS,
                     'CZ_corr ' + qCZ, 'CZ ' + qCZ, 'after_pulse',
                     'tomo1 '+qCZ, 'tomo2 '+qS]
    # base_sequence = num_flux_pulses*['flux ' + qCZ]
    # base_sequence.extend(
    #     ['gate1 ' + qS, 'gate2 ' + qCZ, 'CZ_corr ' + qS, 'CZ_corr ' + qCZ,
    #      'CZ ' + qCZ, 'after_pulse',
    #      'tomo1 '+qCZ, 'tomo2 '+qS])#, 'RO '+RO_target])

    # Calibration points
    # every calibration point is repeated 7 times to have 64 elts in totalb
    # cal_points = [['I '+qCZ, 'I '+qS, 'RO '+RO_target]]*7 + \
    #              [['I '+qCZ, 'X180 '+qS, 'RO '+RO_target]]*7 + \
    #              [['X180 '+qCZ, 'I '+qS, 'RO '+RO_target]]*7 + \
    #              [['X180 '+qCZ, 'X180 '+qS, 'RO '+RO_target]]*7
    cal_points = [['I '+qCZ, 'I '+qS]]*7 + \
                 [['I '+qCZ, 'X180 '+qS]]*7 + \
                 [['X180 '+qCZ, 'I '+qS]]*7 + \
                 [['X180 '+qCZ, 'X180 '+qS]]*7
    operation_dict['I_CZ ' + qCZ] = deepcopy(operation_dict['CZ ' + qCZ])
    operation_dict['I_CZ ' + qCZ]['amplitude'] = 0

    if CZ_disabled:
        operation_dict['CZ'+qCZ]['amplitude'] = 0
    #         operation_dict['CZ '+qCZ]['phase_corr_pulse_amp'] = 0

    #######################################################
    # Creating VZ pulses to compensate for dynamic phases #
    #######################################################
    for qb in [qS, qCZ]:
        if ('CZ_corr ' + qb) not in operation_dict.keys():
            operation_dict['CZ_corr ' + qb] = deepcopy(operation_dict['Z180 ' + qb])
            operation_dict['CZ_corr ' + qb]['refpoint'] = 'end'
    # operation_dict['CZ_corr ' + qCZ]['phase'] = 0
    # operation_dict['CZ_corr ' + qS]['phase'] = 0
    operation_dict['CZ_corr ' + qCZ]['phase'] = operation_dict['CZ ' + qCZ]['dynamic_phase']
    operation_dict['CZ_corr ' + qS]['phase'] = operation_dict['CZ ' + qCZ]['dynamic_phase_target']

    ################
    # Bell states  #
    ################
    if bell_state == 0:  # |Phi_m>=|00>-|11>
        gate1 = 'Y90 ' + qS
        gate2 = 'Y90 ' + qCZ
        after_pulse = 'mY90 ' + qCZ
    elif bell_state == 1:  # |Phi_p>=|00>+|11>
        gate1 = 'Y90 ' + qS
        gate2 = 'mY90 ' + qCZ
        after_pulse = 'mY90 ' + qCZ
    elif bell_state == 2:  # |Psi_m>=|01> - |10>
        gate1 = 'mY90 ' + qS
        gate2 = 'Y90 ' + qCZ
        after_pulse = 'mY90 ' + qCZ
    elif bell_state == 3:  # |Psi_p>=|01> + |10>
        gate1 = 'Y90 ' + qS
        gate2 = 'Y90 ' + qCZ
        after_pulse = 'Y90 ' + qCZ

    # Below are states with the initial pulse on the CP-qubit disabled
    # these are not Bell states but are used for debugging
    elif bell_state == 0+10:  # |00>+|11>
        gate1 = 'Y90 ' + qS
        gate2 = 'I ' + qCZ
        after_pulse = 'mY90 ' + qCZ
    elif bell_state == 1+10:
        gate1 = 'mY90 ' + qS
        gate2 = 'I ' + qCZ
        after_pulse = 'mY90 ' + qCZ
    elif bell_state == 2+10:  # |01> - |10>
        gate1 = 'Y90 ' + qS
        gate2 = 'I ' + qCZ
        after_pulse = 'mY90 ' + qCZ
    elif bell_state == 3+10:
        gate1 = 'mY90 ' + qS
        gate2 = 'I ' + qCZ
        after_pulse = 'mY90 ' + qCZ

    # Below are states with the initial pulse on the SWAP-qubit disabled
    # these are not Bell states but are used for debugging
    elif bell_state == 0 + 20:  # |00>+|11>
        gate1 = 'I ' + qS
        gate2 = 'Y90 ' + qCZ
        after_pulse = 'mY90 ' + qCZ
    elif bell_state == 1 + 20:  # |01> - |10>
        gate1 = 'I ' + qS
        gate2 = 'Y90 ' + qCZ
        after_pulse = 'mY90 ' + qCZ
    elif bell_state == 2 + 20:
        gate1 = 'I ' + qS
        gate2 = 'mY90 ' + qCZ
        after_pulse = 'mY90 ' + qCZ
    elif bell_state == 3 + 20:
        gate1 = 'mY90 ' + qS
        gate2 = 'mY90 ' + qCZ
        after_pulse = 'mY90 ' + qCZ

    #     print('Compensation qCP {:.3f}'.format(
    #         operation_dict['CZ_corr ' + qCZ]['amplitude']))
    #     print('Compensation qS {:.3f}'.format(
    #         operation_dict['SWAP_corr ' + qS]['amplitude']))

    ########################################################
    #  Here the actual pulses of all elements get defined  #
    ########################################################
    # We start by replacing the state prepartion pulses
    base_sequence[base_sequence.index('gate1 ' + qS)] = gate1
    base_sequence[base_sequence.index('gate2 ' + qCZ)] = gate2
    base_sequence[base_sequence.index('after_pulse')] = after_pulse

    seq_pulse_list = []

    for i in range(36):
        tomo_idx_qS = int(i % 6)
        tomo_idx_qCZ = int(((i - tomo_idx_qS)/6) % 6)
        base_sequence[-2] = tomo_list_qCZ[tomo_idx_qCZ]
        base_sequence[-1] = tomo_list_qS[tomo_idx_qS]
        seq_pulse_list += [deepcopy(base_sequence)]
    print(len(cal_points))
    for cal_pulses in cal_points:
        if cal_points_with_flux_pulses:
            #not functional with preflux pulses!
            base_sequence[0] = 'I ' + qS
            base_sequence[1] = 'I ' + qCZ
            base_sequence[4] = 'CZ ' + qCZ
            base_sequence[5] = 'I ' + qCZ
            base_sequence[-2:] = cal_pulses
            seq_pulse_list += [deepcopy(base_sequence)]
        else:
            seq_pulse_list += [cal_pulses]

    for i, pulse_list in enumerate(seq_pulse_list):
        # print('pulse_list ', pulse_list)
        pulses = []
        for p in pulse_list:
            pulses += [operation_dict[p]]
        # print('pulses ', len(pulses))
        pulses += [RO_pars]
        # from pprint import pprint
        # pprint(pulses)
        # print('\n')
        el = multi_pulse_elt(i, station, pulses, sequencer_config)
        if distortion_dict is not None:
            el = fluxpulse_predistortion.distort_qudev(el,distortion_dict)
        el_list.append(el)
        seq.append_element(el, trigger_wait=True)

    if upload:
        station.pulsar.program_awgs(seq, *el_list, verbose=verbose)

    # return seq, seq_pulse_list
    return seq, el_list


def n_qubit_reset(pulse_pars_list, RO_pars, feedback_delay, nr_resets=1,
                  return_seq=False, verbose=False, codeword_indices=None,
                  upload=True):
    n = len(pulse_pars_list)
    seq_name = '{}_qubit_{}_reset_sequence'.format(n, nr_resets)
    seq = sequence.Sequence(seq_name)
    el_list = []

    # Create a dict with the parameters for all the pulses
    pars = RO_pars.copy()
    pars['pulse_delay'] = max(pars['pulse_delay'], -pars['acq_marker_delay'])
    pulse_dict = {'RO': pars}
    for i, pulse_pars in enumerate(pulse_pars_list):
        pars = pulse_pars.copy()
        pulses = add_suffix_to_dict_keys(
            get_pulse_dict_from_pars(pars), ' {}'.format(i))
        pulse_dict.update(pulses)
    spacerpulse = {'pulse_type': 'SquarePulse',
                   'channel': RO_pars['acq_marker_channel'],
                   'amplitude': 0.0,
                   'length': feedback_delay,
                   'pulse_delay': 0}
    pulse_dict.update({'spacer': spacerpulse})

    # create the state-preparation elements and the state reset elements
    for state in range(2 ** n):
        pulses = []
        for qb in range(n):
            if state & (1 << qb):
                pulses += [pulse_dict['X180 {}'.format(qb)].copy()]
            else:
                pulses += [pulse_dict['I {}'.format(qb)].copy()]
            if qb != 0:
                pulses[-1]['refpoint'] = 'simultaneous'
        statename = str(state).zfill(len(str(2**n - 1)))
        el = multi_pulse_elt(state, station, pulses, name='prepare' + statename)
        el_list.append(el)
        el = multi_pulse_elt(state, station, pulses + [pulse_dict['RO'],
                                                       pulse_dict['spacer']],
                             name='reset' + statename, trigger=False)
        el_list.append(el)

    # create the readout element
    pulses = [pulse_dict['RO'], pulse_dict['spacer']]
    el = multi_pulse_elt(state, station, pulses, name='readout', trigger=False)
    el_list.append(el)

    # Create the sequence
    for state in range(2 ** n):
        statename = str(state).zfill(len(str(2 ** n - 1)))
        seq.insert('prepare'+statename, 'prepare'+statename, trigger_wait=True)
        seq.insert('readout' + statename, 'readout',
                   trigger_wait=False, flags={'readout'})
        for i in range(nr_resets):
            seq.insert('codeword' + statename + '_' + str(i), 'codeword',
                       trigger_wait=False)

    # Create the codeword table
    if codeword_indices is None:
        codeword_indices = np.arange(n)
    for state in range(2 ** n):
        statename = str(state).zfill(len(str(2 ** n - 1)))
        codeword = 0
        for qb in range(n):
            if state & (1 << qb):
                codeword |= (1 << codeword_indices[qb])
        seq.codewords[codeword] = 'reset' + statename

    if upload:
        station.pulsar.program_awgs(seq, *el_list, verbose=verbose)

    if return_seq:
        return seq, el_list
    else:
        return seq_name


def two_qubit_parity_measurement(
        q0, q1, q2, feedback_delay=900e-9, prep_sequence=None,
        tomography_basis=('I', 'X180', 'Y90', 'mY90', 'X90', 'mX90'),
        upload=True, verbose=False, return_seq=False):
    """

    |              elem 1               |  elem 2  | elem 3
    
    |q0> |======|---------*------------------------|======|
         | prep |         |                        | tomo |
    |q1> | q0,  |--mY90s--*--*--Y90--meas=====Y180-| q0,  |
         | q2   |            |             ||      | q2   |
    |q2> |======|------------*------------Y180-----|======|
    
    required elements:
        prep_sequence:
            contains everything up to the first readout
        feedback x 2 (for the two readout results):
            contains conditional Y80 on q1 and q2
        tomography x 6**2:
            measure all observables of the two qubits X/Y/Z
    """

    q0n = q0.name
    q1n = q1.name
    q2n = q2.name

    operation_dict = {
        'RO mux': device.get_multiplexed_readout_pulse_dictionary([q0, q1, q2])
    }

    operation_dict.update({
        'I_fb': {'pulse_type': 'SquarePulse',
                 'channel': operation_dict['RO']['acq_marker_channel'],
                 'amplitude': 0.0,
                 'length': feedback_delay,
                 'pulse_delay': 0}
    })
    operation_dict.update(q0.get_operation_dict())
    operation_dict.update(q1.get_operation_dict())
    operation_dict.update(q2.get_operation_dict())

    if prep_sequence is None:
        prep_sequence = ['Y90 ' + q0n, 'Y90s' + q2n]

    # create the elements
    el_list = []

    # main (first) element
    sequence = deepcopy(prep_sequence)
    sequence.append('mY90s ' + q1n)
    sequence.append('CZ ' + q0n + ' ' + q1n)
    sequence.append('CZ ' + q2n + ' ' + q1n)
    sequence.append('Y90 ' + q1n)
    sequence.append('RO ' + q1n)
    sequence.append('I_fb')
    pulse_list = [operation_dict[pulse] for pulse in sequence]
    el_main = multi_pulse_elt(0, station, pulse_list, trigger=True, name='main')
    el_list.append(el_main)

    # feedback elements
    fb_sequence_0 = ['I ' + q2n, 'Is ' + q1n]
    fb_sequence_1 = ['Y180 ' + q2n, 'Y180s ' + q1n]
    pulse_list = [operation_dict[pulse] for pulse in fb_sequence_0]
    el_list.append(multi_pulse_elt(0, station, pulse_list, name='feedback_0',
                                   trigger=False, previous_element=el_main))
    pulse_list = [operation_dict[pulse] for pulse in fb_sequence_1]
    el_fb = multi_pulse_elt(1, station, pulse_list, name='feedback_1',
                            trigger=False, previous_element=el_main)
    el_list.append(el_fb)

    # tomography elements
    tomography_sequences = get_tomography_pulses(q0n, q2n,
                                                 basis_pulses=tomography_basis)
    for i, tomography_sequence in enumerate(tomography_sequences):
        tomography_sequence.append('RO mux')
        pulse_list = [operation_dict[pulse] for pulse in tomography_sequence]
        el_list.append(multi_pulse_elt(i, station, pulse_list, trigger=False,
                                       name='tomography_{}'.format(i),
                                       previous_element=el_fb))

    # create the sequence
    seq_name = 'Two qubit entanglement by parity measurement'
    seq = sequence.Sequence(seq_name)
    seq.codewords[0] = 'feedback_0'
    seq.codewords[1] = 'feedback_1'
    for i in range(len(tomography_basis)**2):
        seq.append('main_{}'.format(i), 'main', trigger_wait=True)
        seq.append('feedback_{}'.format(i), 'codeword', trigger_wait=False)
        seq.append('tomography_{}'.format(i), 'tomography_{}'.format(i),
                   trigger_wait=False)

    if upload:
        station.pulsar.program_awgs(seq, *el_list, verbose=verbose)

    if return_seq:
        return seq, el_list
    else:
        return seq_name

def get_tomography_pulses(*qubit_names, basis_pulses=('I', 'X180', 'Y90',
                                                      'mY90', 'X90', 'mX90')):
    tomo_sequences = [[]]
    for i, qb in enumerate(qubit_names):
        if i == 0:
            qb = ' ' + qb
        else:
            qb = 's ' + qb
        tomo_sequences_new = []
        for sequence in tomo_sequences:
            for pulse in basis_pulses:
                tomo_sequences_new.append(sequence + [pulse+qb])
        tomo_sequences = tomo_sequences_new
    return tomo_sequences






