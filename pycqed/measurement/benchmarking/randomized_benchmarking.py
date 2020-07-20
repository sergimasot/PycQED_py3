import numpy as np
import traceback
from copy import deepcopy
from pycqed.analysis_v3.processing_pipeline import ProcessingPipeline
from pycqed.measurement.calibration.two_qubit_gates import MultiTaskingExperiment
from pycqed.measurement.sweep_points import SweepPoints
from pycqed.measurement.randomized_benchmarking import \
    randomized_benchmarking as rb
import pycqed.measurement.randomized_benchmarking.two_qubit_clifford_group as tqc
from pycqed.analysis_v3 import pipeline_analysis as pla
import logging
log = logging.getLogger(__name__)


class RandomizedBenchmarking(MultiTaskingExperiment):

    kw_for_sweep_points = {
        'nr_seeds': dict(param_name='seeds', unit='',
                         label='Seeds', dimension=0,
                         values_func=lambda ns: np.random.randint(0, 1e8, ns)),
        'cliffords': dict(param_name='cliffords', unit='',
                          label='Nr. Cliffords',
                          dimension=1),
    }

    def __init__(self, task_list=None, sweep_points=None, qubits=None,
                 nr_seeds=None, cliffords=None,
                 interleaved_gate=None, gate_decomposition='HZ', **kw):
        """
        Class to run and analyze the randomized benchmarking experiment on
        one or several qubits in parallel, using the single-qubit Clifford group
        :param task_list: list of dicts; see CalibBuilder docstring
        :param sweep_points: SweepPoints class instance with first sweep
            dimension describing the seeds and second dimension the cliffords
            Ex: [{'seeds': (array([0, 1, 2, 3]), '', 'Nr. Seeds')},
                 {'cliffords': ([0, 4, 10], '', 'Nr. Cliffords')}]
            If it contains only one sweep dimension, this must be the
            cliffords. The seeds will be added automatically.
            If this parameter is provided it will be used for all qubits.
        :param qubits: list of QuDev_transmon class instances
        :param nr_seeds: int specifying the number of times the Clifford
            group should be sampled for each Clifford sequence length.
            If nr_seeds is specified and it does not exist in the SweepPoints
            of each task in task_list, THEN ALL TASKS WILL RECEIVE THE SAME
            PULSES!!!
        :param interleaved_gate: string specifying the interleaved gate in
            pycqed notation (ex: X90, Y180 etc). Gate must be part of the
            Clifford group.
        :param gate_decomposition: string specifying what decomposition to use
            to translate the Clifford elements into applicable pulses.
            Possible choices are 'HZ' or 'XY'.
            See HZ_gate_decomposition and XY_gate_decomposition in
            pycqed\measurement\randomized_benchmarking\clifford_decompositions.py
        :param kw: keyword arguments
            passed to CalibBuilder; see docstring there

        Assumptions:
         - assumes there is one task for each qubit. If task_list is None, it
          will internally create it.
         - in rb_block, it assumes only one parameter is being swept in the
         second sweep dimension (cliffords)
         - interleaved_gate and gate_decomposition should be the same for
         all qubits since otherwise the segments will have very different
         lengths for different qubits
        """
        try:
            self.interleaved_gate = interleaved_gate
            if self.interleaved_gate is not None:
                self.kw_for_sweep_points['nr_seeds'] = [
                    dict(param_name='seeds', unit='',
                         label='Seeds', dimension=0,
                         values_func=lambda ns: np.random.randint(0, 1e8, ns)),
                    dict(param_name='seeds_irb', unit='',
                         label='Seeds', dimension=0,
                         values_func=lambda ns: np.random.randint(0, 1e8, ns))]
            kw['cal_states'] = kw.get('cal_states', '')
            if not hasattr(self, 'experiment_name'):
                self.experiment_name = f'RB_{gate_decomposition}' if \
                    interleaved_gate is not None else \
                    f'SingleQubitIRB_{gate_decomposition}'
            super().__init__(task_list, qubits=qubits,
                             sweep_points=sweep_points,
                             nr_seeds=nr_seeds,
                             cliffords=cliffords, **kw)

            self.identical_pulses = nr_seeds is not None
            self.gate_decomposition = gate_decomposition
            self.preprocessed_task_list = self.preprocess_task_list(**kw)

            # Check if we can apply identical pulses on all qubits in task_list
            # Can only do this if they have identical cliffords array
            if self.identical_pulses:
                unique_clf_sets = np.unique([
                    self.sweep_points.get_sweep_params_property('values', 1, k)
                    for k in self.sweep_points.get_sweep_dimension(1) if
                    k.endswith('cliffords')], axis=0)
                if unique_clf_sets.shape[0] > 1:
                    raise ValueError('Cannot apply identical pulses. '
                                     'Not all qubits have the same Cliffords.'
                                     'To use non-identical pulses, '
                                     'move nr_seeds from keyword arguments '
                                     'into the tasks.')

            self.sequences, self.mc_points = self.sweep_n_dim(
                self.sweep_points, body_block=None,
                body_block_func=self.rb_block, cal_points=self.cal_points,
                ro_qubits=self.meas_obj_names, **kw)
            if self.interleaved_gate is not None:
                seqs_irb, _ = self.sweep_n_dim(
                    self.sweep_points, body_block=None,
                    body_block_func_kw={'interleaved_gate':
                                            self.interleaved_gate},
                    body_block_func=self.rb_block, cal_points=self.cal_points,
                    ro_qubits=self.meas_obj_names, **kw)
                # interleave sequences
                self.sequences, self.mc_points = \
                    self.sequences[0].interleave_sequences(
                        [self.sequences, seqs_irb])
                self.exp_metadata['interleaved_gate'] = self.interleaved_gate
            self.exp_metadata['gate_decomposition'] = self.gate_decomposition
            self.exp_metadata['identical_pulses'] = self.identical_pulses

            self.add_processing_pipeline()
            self.autorun(**kw)

        except Exception as x:
            self.exception = x
            traceback.print_exc()

    def rb_block(self, sp1d_idx, sp2d_idx, **kw):
        pass

    def add_processing_pipeline(self):
        pass

    def run_analysis(self, **kw):
        """
        Runs analysis and stores analysis instance in self.analysis.
        :param kw: keyword_arguments passed to analysis functions;
            see docstrings there
        """
        self.analysis = pla.extract_data_hdf()  # returns a dict
        pla.process_pipeline(self.analysis)


class SingleQubitRandomizedBenchmarking(RandomizedBenchmarking):

    def __init__(self, task_list=None, sweep_points=None, qubits=None, **kw):
        """
        See docstring for RandomizedBenchmarking.
        """
        if task_list is None:
            if qubits is None:
                raise ValueError('Please provide either "qubits" or "task_list"')
            task_list = [{'qb': qb.name} for qb in qubits]

        gate_decomposition = kw.get('gate_decomposition', 'HZ')
        self.experiment_name = f'SingleQubitRB_{gate_decomposition}' if \
            kw.get('interleaved_gate', None) is None else \
            f'SingleQubitIRB_{gate_decomposition}'
        super().__init__(task_list, sweep_points=sweep_points,
                         qubits=qubits, **kw)

    def rb_block(self, sp1d_idx, sp2d_idx, **kw):
        interleaved_gate = kw.get('interleaved_gate', None)
        pulse_op_codes_list = []
        tl = [self.preprocessed_task_list[0]] if self.identical_pulses else \
            self.preprocessed_task_list
        for i, task in enumerate(tl):
            param_name = 'seeds' if interleaved_gate is None else 'seeds_irb'
            seed = task['sweep_points'].get_sweep_params_property(
                'values', 0, param_name)[sp1d_idx]
            clifford = task['sweep_points'].get_sweep_params_property(
                'values', 1, 'cliffords')[sp2d_idx]
            cl_seq = rb.randomized_benchmarking_sequence(
                clifford, seed=seed, interleaved_gate=interleaved_gate)
            pulse_op_codes_list += [rb.decompose_clifford_seq(
                cl_seq, gate_decomp=self.gate_decomposition)]
        rb_block_list = [self.block_from_ops(
            f"rb_{task['qb']}", [f"{p} {task['qb']}" for p in
                                 pulse_op_codes_list[0 if self.identical_pulses
                                 else i]])
            for i, task in enumerate(self.preprocessed_task_list)]

        return self.simultaneous_blocks_align_end(f'sim_rb_{clifford}{sp1d_idx}',
                                                  rb_block_list)

    def add_processing_pipeline(self):
        """
        Creates and adds the analysis processing pipeline to exp_metadata.
        """
        pp = ProcessingPipeline()
        for task in self.preprocessed_task_list:
            cliffords = task['sweep_points'].get_sweep_params_property(
                'values', 1)
            seeds = task['sweep_points'].get_sweep_params_property(
                'values', 0)
            if len(self.cal_points.states) != 0:
                pp.add_node('rotate_iq', keys_in='raw',
                            meas_obj_names=task['qb'],
                            num_keys_out=1)
            pp.add_node('average_data',
                        keys_in='raw' if not self.classified else
                        'previous rotate_iq',
                        shape=(len(cliffords), len(seeds)),
                        meas_obj_names=task['qb'])
            pp.add_node('get_std_deviation',
                        keys_in='raw' if not self.classified else
                        'previous rotate_iq',
                        shape=(len(cliffords), len(seeds)),
                        meas_obj_names=task['qb'])
            pp.add_node('rb_analysis', meas_obj_names=task['qb'],
                        keys_out=None, d=2,
                        keys_in=f'previous average_data',
                        keys_in_std=f'previous get_std_deviation')
        self.exp_metadata.update({'processing_pipeline': pp})


class TwoQubitRandomizedBenchmarking(RandomizedBenchmarking):

    def __init__(self, task_list, sweep_points=None,
                 max_clifford_idx=11520, **kw):
        """
        See docstring for RandomizedBenchmarking.

        :param max_clifford_idx: int that allows to restrict the two qubit
            Clifford that is sampled. Set to 24**2 to only sample the tensor
            product of 2 single qubit Clifford groups.
        """
        self.experiment_name = 'TwoQubitRB' if \
            kw.get('interleaved_gate', None) is None else 'TwoQubitIRB'
        self.max_clifford_idx = max_clifford_idx
        tqc.gate_decomposition = rb.get_clifford_decomposition(
            kw.get('gate_decomposition', 'HZ'))

        for task in task_list:
            for k in ['qb_1', 'qb_2']:
                if not isinstance(task[k], str):
                    task[k] = task[k].name
            if 'prefix' not in task:
                task['prefix'] = f"{task['qb_1']}{task['qb_2']}_"
        kw['for_ef'] = kw.get('for_ef', True)

        super().__init__(task_list, sweep_points=sweep_points, **kw)

    def guess_label(self, **kw):
        """
        Default measurement label.
        """
        suffix = [''.join([task['qb_1'], task['qb_2']])
                  for task in self.task_list]
        suffix = '_'.join(suffix)
        if self.label is None:
            if self.interleaved_gate is None:
                self.label = f'{self.experiment_name}_' \
                             f'{self.gate_decomposition}_{suffix}'
            else:
                self.label = f'{self.experiment_name}_{self.interleaved_gate}_' \
                             f'{self.gate_decomposition}_{suffix}'

    def rb_block(self, sp1d_idx, sp2d_idx, **kw):
        interleaved_gate = kw.get('interleaved_gate', None)
        rb_block_list = []
        for i, task in enumerate(self.preprocessed_task_list):
            param_name = 'seeds' if interleaved_gate is None else 'seeds_irb'
            seed = task['sweep_points'].get_sweep_params_property(
                'values', 0, param_name)[sp1d_idx]
            clifford = task['sweep_points'].get_sweep_params_property(
                'values', 1, 'cliffords')[sp2d_idx]

            cl_seq = rb.randomized_benchmarking_sequence_new(
                clifford, number_of_qubits=2, seed=seed,
                max_clifford_idx=kw.get('max_clifford_idx',
                                        self.max_clifford_idx),
                interleaving_cl=interleaved_gate)

            qb_1 = task['qb_1']
            qb_2 = task['qb_2']
            seq_blocks = []
            single_qb_gates = {qb_1: [], qb_2: []}
            for k, idx in enumerate(cl_seq):
                pulse_tuples_list = tqc.TwoQubitClifford(idx).gate_decomposition
                for j, pulse_tuple in enumerate(pulse_tuples_list):
                    if isinstance(pulse_tuple[1], list):
                        seq_blocks.append(
                            self.simultaneous_blocks(
                                f'blk{k}_{j}', [
                            self.block_from_ops(f'blk{k}_{j}_{qbn}', gates)
                                    for qbn, gates in single_qb_gates.items()]))
                        single_qb_gates = {qb_1: [], qb_2: []}
                        seq_blocks.append(self.block_from_ops(
                            f'blk{k}_{j}_cz',
                            f'{kw.get("cz_pulse_name", "CZ")} {qb_1} {qb_2}'))
                    else:
                        qb_name = qb_1 if '0' in pulse_tuple[1] else qb_2
                        pulse_name = pulse_tuple[0]
                        single_qb_gates[qb_name].append(
                            pulse_name + ' ' + qb_name)

            seq_blocks.append(
                self.simultaneous_blocks(
                    f'blk{i}', [
                        self.block_from_ops(f'blk{i}{qbn}', gates)
                        for qbn, gates in single_qb_gates.items()]))
            rb_block_list += [self.sequential_blocks(f'rb_block{i}', seq_blocks)]

        return self.simultaneous_blocks_align_end(
            f'sim_rb_{sp2d_idx}_{sp1d_idx}', rb_block_list)

    def add_processing_pipeline(self):
        """
        Creates and adds the analysis processing pipeline to exp_metadata.
        """
        pp = ProcessingPipeline()
        for task in self.preprocessed_task_list:
            cliffords = task['sweep_points'].get_sweep_params_property(
                'values', 1)
            seeds = task['sweep_points'].get_sweep_params_property(
                'values', 0)
            if len(self.cal_points.states) != 0:
                pp.add_node('rotate_iq', keys_in='raw',
                            meas_obj_names=[task['qb_1'], task['qb_2']],
                            num_keys_out=1)
            pp.add_node('average_data',
                        keys_in='raw' if not self.classified else
                        'previous rotate_iq',
                        shape=(len(cliffords), len(seeds)),
                        meas_obj_names=[task['qb_1'], task['qb_2']],)
            pp.add_node('get_std_deviation',
                        keys_in='raw' if not self.classified else
                        'previous rotate_iq',
                        shape=(len(cliffords), len(seeds)),
                        meas_obj_names=[task['qb_1'], task['qb_2']],)
            pp.add_node('rb_analysis',
                        meas_obj_names=[task['qb_1'], task['qb_2']],
                        keys_out=None, d=4,
                        keys_in=f'previous average_data',
                        keys_in_std=f'previous get_std_deviation')
        self.exp_metadata.update({'processing_pipeline': pp})