'''
    File:               waveform_flux.py
    Author:             Filip Malinowski and Adriaan Rol
    Purpose:            generate flux waveforms that require knowledge
        of the qubit Hamiltonian.
    Prerequisites:
    Usage:
    Bugs:

For more basic waveforms see e.g., waveforms.py
'''
import logging
import scipy.interpolate
import numpy as np

log = logging.getLogger(__name__)


def martinis_flux_pulse(length: float,
                        theta_i: float, theta_f: float,
                        lambda_2: float, lambda_3: float = 0, lambda_4: float = 0,
                        sampling_rate: float = 2.4e9):
    """
    Returns the pulse specified by Martinis and Geller as θ(t) specified in
        Phys. Rev. A 90 022307 (2014).
    Note that θ still needs to be transformed into detuning from the
    interaction and into AWG amplitude V(t).

        θ(τ) = θ_i + Σ_{n=1}^N  λ_n*(1-cos(n*2*pi*τ/τ_p))

    Args:
        length      :   lenght of the waveform (s)
        lambda_2    :   lambda coeffecients
        lambda_3    :
        lambda_3    :
        theta_i     :   initial angle of interaction (rad).
        theta_f     :   final angle of the interaction (rad).
        sampling_rate : sampling rate of AWG in (Hz)

    This waveform is generated in several steps
        1. Generate a time grid, may include fine sampling.
        2. Generate θ(τ) using eqs 15 and 16
        3. Transform from proper time "τ" to real time "t" using interpolation

    """
    if theta_f < theta_i:
        log.debug(
            'theta_f ({:.2f} deg) < theta_i ({:.2f} deg):'.format(
                np.rad2deg(theta_f), np.rad2deg(theta_i))
            + 'final coupling weaker than initial coupling')
        theta_f = np.clip(theta_f, theta_i, np.pi - .01)

    # 1. Generate a time grid, may include fine sampling.

    # Pulse is generated at a denser grid to allow for good interpolation
    # N.B. Not clear why interpolation is needed at all... -MAR July 2018
    fine_sampling_factor = 2  # 10
    nr_samples = int(np.round((length) * sampling_rate * fine_sampling_factor))
    rounded_length = nr_samples / (fine_sampling_factor * sampling_rate)
    tau_step = 1 / (fine_sampling_factor * sampling_rate)  # denser points
    # tau is a virtual time/proper time
    taus = np.arange(0, rounded_length - tau_step / 2, tau_step)
    # -tau_step/2 is to make sure final pt is excluded

    # lambda_1 is scaled such that the final ("center") angle is theta_f
    # Determine lambda_1 using the constraint set by eq 16 from Martinis 2014
    lambda_1 = (theta_f - theta_i) / (2) - lambda_3

    # 2. Generate θ(τ) using eqs 15 and 16
    theta_wave = np.ones(nr_samples) * theta_i
    theta_wave += lambda_1 * (1 - np.cos(2 * np.pi * taus / rounded_length))
    theta_wave += lambda_2 * (1 - np.cos(4 * np.pi * taus / rounded_length))
    theta_wave += lambda_3 * (1 - np.cos(6 * np.pi * taus / rounded_length))
    theta_wave += lambda_4 * (1 - np.cos(8 * np.pi * taus / rounded_length))

    # Clip wave to [theta_i, pi] to avoid poles in the wave expressed in freq
    theta_wave_clipped = np.clip(theta_wave, theta_i, np.pi - .01)
    if not np.array_equal(theta_wave, theta_wave_clipped):
        log.debug(
            'Martinis flux wave form has been clipped to [{}, 180 deg]'
            .format(np.rad2deg(theta_i)))

    # 3. Transform from proper time τ to real time t using interpolation, eqs. 17-20
    t = np.array([np.trapz(np.sin(theta_wave_clipped)[: i + 1],
                           dx=1 / (fine_sampling_factor * sampling_rate))
                  for i in range(len(theta_wave_clipped))])

    # Interpolate pulse at physical sampling distance
    t_samples = np.arange(0, length, 1 / sampling_rate)
    # Scaling factor for time-axis to get correct pulse length again
    scale = t[-1] / t_samples[-1]
    interp_wave = scipy.interpolate.interp1d(
        # taus, theta_wave_clipped, bounds_error=False, # this line by-passes interpolation
        t/scale, theta_wave_clipped, bounds_error=False, # this line enables interpolation
        fill_value='extrapolate')(t_samples)
    # Theta is returned in radians here
    return np.nan_to_num(interp_wave)

def martinis_flux_pulse_v2(length: float,
                           theta_i: float, theta_f: float,
                           lambda_1: float = 0,
                           lambda_2: float = 0, lambda_3: float = 0, lambda_4: float = 0,
                           step_length: float = 10e-9, step_height: float = 0,
                           step_max: float = np.pi/200, step_first: bool = False,
                           apply_wait_time: bool = True,
                           theta_f_must_be_above: bool = True,
                           sampling_rate: float = 2.4e9, interpolate=False):
    """
    Version reviewed by Ramiro, following design agreements with Miguel and Leo
    Returns the pulse specified by Martinis and Geller as θ(t) specified in
        Phys. Rev. A 90 022307 (2014).
    Note that θ still needs to be transformed into detuning from the
    interaction and into AWG amplitude V(t).

        θ(τ) = θ_i + Σ_{n=1}^N  λ_n*(1-cos(n*2*pi*τ/τ_p))

    Args:
        length      :   lenght of the waveform (s)
        lambda_2    :   lambda coeffecients
        lambda_3    :
        lambda_3    :
        theta_i     :   initial angle of interaction (rad).
        theta_f     :   final angle of the interaction (rad).
        sampling_rate : sampling rate of AWG in (Hz)

    This waveform is generated in several steps
        1. Generate a time grid, may include fine sampling.
        2. Generate θ(τ) using eqs 15 and 16
        3. Transform from proper time "τ" to real time "t" using interpolation

    """
    if (theta_f < theta_i) and theta_f_must_be_above:
        log.debug(
            'theta_f ({:.2f} deg) < theta_i ({:.2f} deg):'.format(
                np.rad2deg(theta_f), np.rad2deg(theta_i))
            + 'final coupling weaker than initial coupling')
        theta_f = np.clip(theta_f, theta_i, np.pi - .01)

    # 1. Generate a time grid, may include fine sampling.

    # Pulse is generated at a denser grid to allow for good interpolation
    # N.B. Not clear why interpolation is needed at all... -MAR July 2018

    fine_sampling_factor = 1  # 10
    nr_samples = int(np.round((length) * sampling_rate * fine_sampling_factor))
    rounded_length = nr_samples / (fine_sampling_factor * sampling_rate)
    """
    New lines after ensuring sample rounding
    """
    # fine_sampling_factor = 1
    # nr_samples = int(np.ceil(length * (fine_sampling_factor * sampling_rate)))
    # rounded_length = nr_samples / (sampling_rate * fine_sampling_factor)

    tau_step = 1 / (fine_sampling_factor * sampling_rate)  # denser points
    # tau is a virtual time/proper time
    taus = np.arange(0, rounded_length - tau_step / 2, tau_step)

    # lambda_1 is scaled such that the final ("center") angle is theta_f
    # Determine lambda_1 using the constraint set by eq 16 from Martinis 2014
    # -tau_step/2 is to make sure final pt is excluded
    lambda_0 = 1 - lambda_1

    norm_odd_lambdas = lambda_1 + lambda_3 + lambda_0
    desired_norm = 1/2#(theta_f - theta_i) / 2
    factor_norm = 1
    if np.abs(norm_odd_lambdas)>0:
        factor_norm = (desired_norm/norm_odd_lambdas)
    lambda_1 = lambda_1 * factor_norm
    lambda_3 = lambda_3 * factor_norm

    # 2. Generate θ(τ) using eqs 15 and 16
    dtheta_vec = lambda_0 * np.ones(nr_samples)
    dtheta_vec += lambda_1 * (1 - np.cos(2 * np.pi * taus / rounded_length))
    dtheta_vec += lambda_2 * (1 - np.cos(4 * np.pi * taus / rounded_length))
    dtheta_vec += lambda_3 * (1 - np.cos(6 * np.pi * taus / rounded_length))
    dtheta_vec += lambda_4 * (1 - np.cos(8 * np.pi * taus / rounded_length))
    theta_wave = np.ones(nr_samples) * theta_i
    theta_wave += dtheta_vec*(theta_f-theta_i)

    #before clipping the wave:
    nr_samples_step = int(np.round(step_length * sampling_rate))
    l_half = int(len(theta_wave)/2)
    step_vec = np.ones(l_half)*step_max*step_height + theta_i
    if apply_wait_time:
        if step_first: # step goes on the first half
            theta_wave[:l_half] = np.max([theta_wave[:l_half],step_vec],axis=0)
        else: # step goes on the second half
            theta_wave[-l_half:] = np.max([theta_wave[-l_half:],step_vec],axis=0)

    # Clip wave to [theta_i, pi] to avoid poles in the wave expressed in freq
    if theta_f_must_be_above:
        clip_min = theta_i
    else:
        clip_min = 0
    theta_wave_clipped = np.clip(theta_wave, clip_min, np.pi - .01)
    if not np.array_equal(theta_wave, theta_wave_clipped):
        log.debug(
            'Martinis flux wave form has been clipped to [{}, 180 deg]'
            .format(np.rad2deg(clip_min)))


    # Interpolate pulse at physical sampling distance
    t_samples = np.arange(0, length, 1 / sampling_rate)

    if interpolate:
        # 3. Transform from proper time τ to real time t using interpolation, eqs. 17-20
        t = np.array([np.trapz(np.sin(theta_wave_clipped)[: i + 1],
                               dx=1 / (fine_sampling_factor * sampling_rate))
                      for i in range(len(theta_wave_clipped))])
        # Scaling factor for time-axis to get correct pulse length again
        scale = t[-1] / t_samples[-1]
        t_interp = t/scale
    else:
        t_interp = taus
    interp_wave = scipy.interpolate.interp1d(
        t_interp, theta_wave_clipped, bounds_error=False,
        fill_value='extrapolate')(t_samples)
    # Theta is returned in radians here
    return np.nan_to_num(interp_wave)

def eps_to_theta(eps: float, g: float):
    """
    Converts ε into θ as defined in Phys. Rev. A 90 022307 (2014)

        θ = arctan(Hx/Hz)
        θ = arctan(2*g/ε)

    args:
        ε: detuning
        g: coupling strength
    returns:
        θ: interaction angle (radian)
    """
    # Ignore divide by zero as it still gives a meaningful angle
    with np.errstate(divide='ignore'):
        theta = np.arctan(np.divide(2 * g, eps))
    return theta


def theta_to_eps(theta: float, g: float):
    """
    Converts θ into ε as defined in Phys. Rev. A 90 022307 (2014)
        Hz = Hx/tan(θ)
        ε = 2g/tan(θ)

    args:
        θ: interaction angle (radian)
        g: coupling strength
    returns:
        ε: detuning
    """
    eps = 2 * g / np.tan(theta)
    return eps
