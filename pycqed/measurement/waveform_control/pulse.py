"""
The definition of the base pulse object that generates pulse waveforms.

The pulse objects represent an analytical form of the pulses, and can generate
the waveforms for the time-values that are passed in to its waveform generation
function.

The actual pulse implementations are defined in separate modules,
e.g. pulse_library.py.

The module variable `pulse_libraries` is a
"""

import numpy as np
import scipy as sp

pulse_libraries = set()
"""set of module: The set of pulse implementation libraries.

These will be searched when a pulse dictionary is converted to the pulse object.
The pulse class is stored as a string in a pulse dictionary.

Each pulse library module should add itself to this set, e.g.
>>> import sys
>>> from pyceqed.measurement.waveform_control import pulse
>>> pulse.pulse_libraries.add(sys.modules[__name__])
"""


class Pulse:
    """
    The pulse base class.

    Args:
        name (str): The name of the pulse, used for referencing to other pulses
            in a sequence. Typically generated automatically by the `Segment`
            class.
        element_name (str): Name of the element the pulse should be played in.
        codeword (int or 'no_codeword'): The codeword that the pulse belongs in.
            Defaults to 'no_codeword'.
        length (float, optional): The length of the pulse instance in seconds.
            Defaults to 0.
        channels (list of str, optional): A list of channel names that the pulse
            instance generates waveforms form. Defaults to empty list.
    """

    def __init__(self, name, element_name, **kw):

        self.name = name
        self.element_name = element_name
        self.codeword = kw.pop('codeword', 'no_codeword')
        self.pulse_off = kw.pop('pulse_off', False)
        self.truncation_length = kw.pop('truncation_length', None)
        self.truncation_decay_sigma = kw.pop('truncation_decay_sigma', 0)
        self.truncation_decay_nr_sigma = kw.pop('truncation_decay_nr_sigma',
                                                None)
        self.nr_points_spline = kw.pop('nr_points_spline', 0)
        self.crosstalk_cancellation_channels = []
        self.crosstalk_cancellation_mtx = None
        self.crosstalk_cancellation_shift_mtx = None

        # Set default pulse_params and overwrite with params in keyword argument
        # list if applicable
        for k, v in self.pulse_params().items():
            setattr(self, k, kw.get(k, v))

        self._t0 = None

    def truncate_wave(self, tvals, wave):
        """
        Truncate a waveform.
        :param tvals: sample start times for the channels to generate
            the waveforms for
        :param wave: waveform sample amplitudes corresponding to tvals
        :return: truncated waveform if truncation_length attribute is not None,
            else unmodified waveform
        """
        trunc_len = getattr(self, 'truncation_length', None)
        if trunc_len is None:
            return wave

        # truncation_length should be (n+0.5) samples to avoid
        # rounding errors
        mask = tvals <= (tvals[0] + trunc_len)
        tr_dec_sigma = getattr(self, 'truncation_decay_sigma')
        nr_points_spline = getattr(self, 'nr_points_spline')
        if tr_dec_sigma > 0:
            tr_dec_nr_sigma = getattr(self, 'truncation_decay_nr_sigma')
            if tr_dec_nr_sigma is None:
                raise ValueError('Please specify truncation_decay_nr_sigma.')
            tr_dec_length = tr_dec_sigma * tr_dec_nr_sigma

            # add slow Gaussian decay after truncation
            decay_func = lambda sigma, t, amp, offset: \
                amp * 0.5 * (1 - sp.special.erf(
                    (t - offset) / np.sqrt(2) / sigma))
            ts_start_idx = np.count_nonzero(mask) - 1
            gauss_start_idx = ts_start_idx + nr_points_spline//2
            wave_end = decay_func(tr_dec_sigma, tvals, wave[gauss_start_idx],
                                  tvals[0] + trunc_len + tr_dec_length/2)[
                       gauss_start_idx:]
            wave = np.concatenate([wave[:gauss_start_idx], wave_end])

            if nr_points_spline > 0:
                # add cubic spline to smooth out kink at the start of truncation
                spline_func = lambda t, a, b, c, d: a*t**3 + b*t**2 + c*t + d
                # define spline start and end
                spl_start_idx = ts_start_idx
                spl_stop_idx = ts_start_idx + nr_points_spline
                t_spline = tvals[spl_start_idx:spl_stop_idx]
                # compute a, b, c, d of spline function by solving linear
                # equation such that the points at spl_start_idx,
                # spl_start_idx - 1, spl_stop_idx, spl_stop_idx + 1 are part of
                # the spline
                A = []
                B = []
                for offset in [-1, 0]:
                    A += [[tvals[spl_start_idx+offset]**3,
                           tvals[spl_start_idx+offset]**2,
                           tvals[spl_start_idx+offset],
                           1]]
                    B += [wave[spl_start_idx+offset]]
                for offset in [0, 1]:
                    A += [[tvals[spl_stop_idx+offset]**3,
                           tvals[spl_stop_idx+offset]**2,
                           tvals[spl_stop_idx+offset],
                           1]]
                    B += [wave[spl_stop_idx+offset]]
                wave = np.concatenate([wave[:spl_start_idx],
                                       spline_func(t_spline,
                                                   *np.linalg.solve(
                                                       np.array(A),
                                                       np.array(B))),
                                       wave[spl_stop_idx:]])
        else:
            wave *= mask
        return wave

    def waveforms(self, tvals_dict):
        """Generate waveforms for any channels of the pulse.

        Calls `Pulse.chan_wf` internally.

        Args:
            tvals_dict (dict of np.ndarray): a dictionary of the sample
                start times for the channels to generate the waveforms for.

        Returns:
            dict of np.ndarray: a dictionary of the voltage-waveforms for the
            channels that are both in the tvals_dict and in the
            pulse channels list.
        """
        wfs_dict = {}
        for c in self.channels:
            if c in tvals_dict and c not in \
                    self.crosstalk_cancellation_channels:
                wfs_dict[c] = self.chan_wf(c, tvals_dict[c])
                if getattr(self, 'pulse_off', False):
                    wfs_dict[c] = np.zeros_like(wfs_dict[c])
                wfs_dict[c] = self.truncate_wave(tvals_dict[c], wfs_dict[c])
        for c in self.crosstalk_cancellation_channels:
            if c in tvals_dict:
                idx_c = self.crosstalk_cancellation_channels.index(c)
                wfs_dict[c] = np.zeros_like(tvals_dict[c])
                if not getattr(self, 'pulse_off', False):
                    for c2 in self.channels:
                        if c2 not in self.crosstalk_cancellation_channels:
                            continue
                        idx_c2 = self.crosstalk_cancellation_channels.index(c2)
                        factor = self.crosstalk_cancellation_mtx[idx_c, idx_c2]
                        shift = self.crosstalk_cancellation_shift_mtx[
                            idx_c, idx_c2] \
                            if self.crosstalk_cancellation_shift_mtx is not \
                            None else 0
                        wfs_dict[c] += factor * self.chan_wf(
                            c2, tvals_dict[c] - shift)
                    wfs_dict[c] = self.truncate_wave(tvals_dict[c], wfs_dict[c])
        return wfs_dict

    def masked_channels(self):
        channel_mask = getattr(self, 'channel_mask', None)
        if channel_mask is None:
            channels = self.channels
        else:
            channels = [ch for m, ch in zip(channel_mask, self.channels) if m]
        return set(channels) | set(self.crosstalk_cancellation_channels)

    def pulse_area(self, channel, tvals):
        """
        Calculates the area of a pulse on the given channel and time-interval.

        Args:
            channel (str): The channel name
            tvals (np.ndarray): the sample start-times

        Returns:
            float: The pulse area.
        """
        if getattr(self, 'pulse_off', False):
            return 0

        if channel in self.crosstalk_cancellation_channels:
            # if channel is a crosstalk cancellation channel, then the area
            # of all flux pulses applied on this channel are
            # retrieved and added together
            wfs = [] # list of waveforms, area computed in return statement
            idx_c = self.crosstalk_cancellation_channels.index(channel)
            if not getattr(self, 'pulse_off', False):
                for c2 in self.channels:
                    if c2 not in self.crosstalk_cancellation_channels:
                        continue
                    idx_c2 = self.crosstalk_cancellation_channels.index(c2)
                    factor = self.crosstalk_cancellation_mtx[idx_c, idx_c2]
                    wfs.append(factor * self.chan_wf( c2, tvals))
        elif channel in self.channels:
            wfs = self.waveforms({channel: tvals})[channel]
        else:
            wfs = np.zeros_like(tvals)
        dt = tvals[1] - tvals[0]

        return np.sum(wfs) * dt

    def algorithm_time(self, val=None):
        """
        Getter and setter for the start time of the pulse.
        """
        if val is None:
            return self._t0
        else:
            self._t0 = val

    def element_time(self, element_start_time):
        """
        Returns the pulse time in the element frame.
        """
        return self.algorithm_time() - element_start_time

    def hashables(self, tstart, channel):
        """Abstract base method for a list of hash-elements for this pulse.

        The hash-elements must uniquely define the returned waveform as it is
        used to determine whether waveforms can be reused.

        Args:
            tstart (float): start time of the element
            channel (str): channel name

        Returns:
            list: A list of hash-elements
        """
        raise NotImplementedError('hashables() not implemented for {}'
                                  .format(str(type(self))[1:-1]))

    def chan_wf(self, channel, tvals):
        """Abstract base method for generating the pulse waveforms.

        Args:
            channel (str): channel name
            tvals (np.ndarray): the sample start times

        Returns:
            np.ndarray: the waveforms corresponding to `tvals` on
            `channel`
        """
        raise NotImplementedError('chan_wf() not implemented for {}'
                                  .format(str(type(self))[1:-1]))

    @classmethod
    def pulse_params(cls):
        """
        Returns a dictionary of pulse parameters and initial values.
        """
        raise NotImplementedError('pulse_params() not implemented for your pulse')
