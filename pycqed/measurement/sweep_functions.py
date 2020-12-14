import logging
import time
import numpy as np
from pycqed.measurement import mc_parameter_wrapper
import qcodes
from pycqed.measurement.waveform_control.pulse_library import GaussFilteredCosIQPulse


class Sweep_function(object):
    '''
    sweep_functions class for MeasurementControl(Instrument)
    '''

    def __init__(self, **kw):
        self.set_kw()

    def set_kw(self, **kw):
        '''
        convert keywords to attributes
        '''
        for key in list(kw.keys()):
            exec('self.%s = %s' % (key, kw[key]))

    def prepare(self, **kw):
        pass

    def finish(self, **kw):
        pass

    # note that set_paramter is only actively used in soft sweeps.
    # it is added here so that performing a "hard 2D" experiment
    # (see tests for MC) the missing set_parameter in the hard sweep does not
    # lead to unwanted errors
    def set_parameter(self, val):
        '''
        Set the parameter(s) to be sweeped. Differs per sweep function
        '''
        pass


class Soft_Sweep(Sweep_function):
    def __init__(self, **kw):
        self.set_kw()
        self.sweep_control = 'soft'


##############################################################################


class Elapsed_Time_Sweep(Soft_Sweep):
    """
    A sweep function to do a measurement periodically.
    Set the sweep points to the times at which you want to probe the
    detector function.
    """

    def __init__(self,
                 sweep_control='soft',
                 as_fast_as_possible: bool = False,
                 **kw):
        super().__init__()
        self.sweep_control = sweep_control
        self.name = 'Elapsed_Time_Sweep'
        self.parameter_name = 'Time'
        self.unit = 's'
        self.as_fast_as_possible = as_fast_as_possible
        self.time_first_set = None

    def set_parameter(self, val):
        if self.time_first_set is None:
            self.time_first_set = time.time()
            return 0
        elapsed_time = time.time() - self.time_first_set
        if self.as_fast_as_possible:
            return elapsed_time

        if elapsed_time > val:
            logging.warning(
                'Elapsed time {:.2f}s larger than desired {:2f}s'.format(
                    elapsed_time, val))
            return elapsed_time

        while (time.time() - self.time_first_set) < val:
            pass  # wait
        elapsed_time = time.time() - self.time_first_set
        return elapsed_time


class None_Sweep(Soft_Sweep):
    def __init__(self,
                 sweep_control='soft',
                 sweep_points=None,
                 name: str = 'None_Sweep',
                 parameter_name: str = 'pts',
                 unit: str = 'arb. unit',
                 **kw):
        super(None_Sweep, self).__init__()
        self.sweep_control = sweep_control
        self.name = name
        self.parameter_name = parameter_name
        self.unit = unit
        self.sweep_points = sweep_points

    def set_parameter(self, val):
        '''
        Set the parameter(s) to be swept. Differs per sweep function
        '''
        pass


class None_Sweep_idx(None_Sweep):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.num_calls = 0

    def set_parameter(self, val):
        self.num_calls += 1


class Delayed_None_Sweep(Soft_Sweep):
    def __init__(self, sweep_control='soft', delay=0, mode='cycle_delay',
                 **kw):
        super().__init__()
        self.sweep_control = sweep_control
        self.name = 'None_Sweep'
        self.parameter_name = 'pts'
        self.unit = 'arb. unit'
        self.delay = delay
        self.time_last_set = 0
        self.mode = mode
        if delay > 60:
            logging.warning(
                'setting a delay of {:.g}s are you sure?'.format(delay))

    def set_parameter(self, val):
        '''
        Set the parameter(s) to be sweeped. Differs per sweep function
        '''
        if self.mode != 'cycle_delay':
            self.time_last_set = time.time()
        while (time.time() - self.time_last_set) < self.delay:
            pass  # wait
        if self.mode == 'cycle_delay':
            self.time_last_set = time.time()


###############################################################################
####################          Hardware Sweeps      ############################
###############################################################################


class Hard_Sweep(Sweep_function):
    def __init__(self, **kw):
        super().__init__()
        self.sweep_control = 'hard'
        self.parameter_name = 'None'
        self.name = 'Hard_Sweep'
        self.unit = 'a.u.'

    def start_acquistion(self):
        pass

    def set_parameter(self, value):
        logging.warning('set_parameter called for hardware sweep.')


class Segment_Sweep(Hard_Sweep):
    def __init__(self, **kw):
        super().__init__()
        self.parameter_name = 'Segment index'
        self.name = 'Segment_Sweep'
        self.unit = ''

class multi_sweep_function(Soft_Sweep):
    '''
    cascades several sweep functions into a single joint sweep functions.
    '''

    def __init__(self,
                 sweep_functions: list,
                 parameter_name=None,
                 name=None,
                 **kw):
        self.set_kw()
        self.sweep_functions = sweep_functions
        self.sweep_control = 'soft'
        self.name = name or 'multi_sweep'
        self.unit = sweep_functions[0].unit
        self.parameter_name = parameter_name or 'multiple_parameters'
        for i, sweep_function in enumerate(sweep_functions):
            if self.unit.lower() != sweep_function.unit.lower():
                raise ValueError('units of the sweepfunctions are not equal')

    def set_parameter(self, val):
        for sweep_function in self.sweep_functions:
            sweep_function.set_parameter(val)


class two_par_joint_sweep(Soft_Sweep):
    """
    Allows jointly sweeping two parameters while preserving their
    respective ratios.
    Allows par_A and par_B to be arrays of parameters
    """

    def __init__(self, par_A, par_B, preserve_ratio: bool = True, **kw):
        self.set_kw()
        self.unit = par_A.unit
        self.sweep_control = 'soft'
        self.par_A = par_A
        self.par_B = par_B
        self.name = par_A.name
        self.parameter_name = par_A.name
        if preserve_ratio:
            try:
                self.par_ratio = self.par_B.get() / self.par_A.get()
            except:
                self.par_ratio = (
                    self.par_B.get_latest() / self.par_A.get_latest())
        else:
            self.par_ratio = 1

    def set_parameter(self, val):
        self.par_A.set(val)
        self.par_B.set(val * self.par_ratio)


class SHF_Sweep(Soft_Sweep):

    def __init__(self,
                 shf, shf_lo_freq, qb,
                 name=None,
                 parameter_name=None,
                 unit=None):
        super().__init__()
        self.shf = shf
        self.shf_lo_freq = shf_lo_freq
        self.qb = qb
        self.name = name
        self.parameter_name = parameter_name
        self.unit = unit

    def prepare(self, *args, **kwargs):
        print('SHFQA Sweep Preperation')

    def finish(self, *args, **kwargs):
        print('SHFQA Sweep Finish')

    def set_parameter(self, val):

        # calculate mod freq
        f_mod = val - self.shf_lo_freq

        # uplaod weights
        tbase = np.arange(0, 4097 / 2.0e9, 1 / 2.0e9)
        theta = self.qb.acq_IQ_angle()
        cosI = np.array(np.cos(2 * np.pi * f_mod * tbase + theta))
        sinI = np.array(np.sin(2 * np.pi * f_mod * tbase + theta))
        c1 = self.qb.acq_I_channel()
        c2 = self.qb.acq_Q_channel()
        self.shf[0].setVector(f"/{self.shf[1]}/QAS/0/INTEGRATION/SIGINS/0/WEIGHTS/{c1}/REAL", cosI.astype("float"))
        self.shf[0].setVector(f"/{self.shf[1]}/QAS/0/INTEGRATION/SIGINS/0/WEIGHTS/{c2}/REAL", sinI.astype("float"))
        self.shf[0].setVector(f"/{self.shf[1]}/QAS/0/INTEGRATION/SIGINS/0/WEIGHTS/{c1}/IMAG", sinI.astype("float"))
        self.shf[0].setVector(f"/{self.shf[1]}/QAS/0/INTEGRATION/SIGINS/0/WEIGHTS/{c2}/IMAG", cosI.astype("float"))

        # upload waveform
        tvals = np.arange(0, 8192 / 2.0e9, 1 / 2.0e9)
        ro_pulse = GaussFilteredCosIQPulse(I_channel=0, Q_channel=1, element_name='ro_pulse')
        ro_pulse.amplitude = self.qb.get_ro_pars()['amplitude']
        ro_pulse.pulse_length = self.qb.get_ro_pars()['pulse_length']
        ro_pulse.mod_frequency = f_mod
        ro_pulse.gaussian_filter_sigma = self.qb.get_ro_pars()['gaussian_filter_sigma']
        ro_pulse.nr_sigma = self.qb.get_ro_pars()['nr_sigma']
        ro_pulse.phase_lock = self.qb.get_ro_pars()['phase_lock']
        I_wave = ro_pulse.chan_wf(0, tvals)
        Q_wave = ro_pulse.chan_wf(1, tvals)
        wave_IQ = np.zeros(2 * 8192)
        wave_null = np.zeros(2 * 8192)

        A_wave = 129760
        wave_IQ[::2] = I_wave * A_wave
        wave_IQ[1::2] = -Q_wave * A_wave

        self.shf[0].setVector(f'/{self.shf[1]}/RAW/AWGS/0/WAVEFORM/WAVES/{0}', wave_IQ.astype("uint32"))

        for idx in range(1, 10):
            self.shf[0].setVector(f'/{self.shf[1]}/RAW/AWGS/0/WAVEFORM/WAVES/{idx}', wave_null.astype("uint32"))


class Offset_Sweep(Soft_Sweep):
    """A sweep soft sweep function that calls an other sweep function with
    an offset."""

    def __init__(self,
                 sweep_function,
                 offset,
                 name=None,
                 parameter_name=None,
                 unit=None):
        super().__init__()
        if isinstance(sweep_function, qcodes.Parameter):
            sweep_function = mc_parameter_wrapper.wrap_par_to_swf(
                sweep_function)
        if sweep_function.sweep_control != 'soft':
            raise ValueError('Offset_Sweep: Only software sweeps supported')
        self.sweep_function = sweep_function
        self.offset = offset
        self.sweep_control = sweep_function.sweep_control
        if parameter_name is None:
            self.parameter_name = sweep_function.parameter_name + \
                ' {:+} {}'.format(-offset, sweep_function.unit)
        else:
            self.parameter_name = parameter_name
        if name is None:
            self.name = sweep_function.name
        else:
            self.name = name
        if unit is None:
            self.unit = sweep_function.unit
        else:
            self.unit = unit

    def prepare(self, *args, **kwargs):
        self.sweep_function.prepare(*args, **kwargs)

    def finish(self, *args, **kwargs):
        self.sweep_function.finish(*args, **kwargs)

    def set_parameter(self, val):
        self.sweep_function.set_parameter(val + self.offset)
