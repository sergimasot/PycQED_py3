'''
Part of the 'new' analysis toolbox.
This should contain all the functions that where previously/are now contained
in modules/analysis/analysis_toolbox.py in the Analysis tools section.
To give a feeling of what functions belong here, the old a_tools can be
roughly split into
- file-handling tools
- data manipulation tools
- plotting tools

'''
import numpy as np


def count_rounds_to_error(series):
    '''
    returns the index of the first entry that is different
    from the initial value.

    input:
        series : array or list
    output:
        rounds_since_change: list

    Returns NAN if no error is found
    NOTE: superceded by count_rtf_and_term_cond()
    '''
    last_s = series[0]
    for i, s in enumerate(series):
        if s == last_s:
            last_s = s
        else:
            return i
    print('Warning did not find any error')
    return np.NAN


def count_rtf_and_term_cond(series, only_count_min_1=False,
                            return_termination_condition=True):
    '''
    returns the index of the first entry that is different
    from the initial value.

    input:
        series : array or list
    output:
        rounds to failure (int), termination condition (string)

    Returns the lenght of the timetrace +1  if no error is found
    '''
    rtf = len(series) + 1
    termination_condition = None
    initial_s = series[0]

    for i, s in enumerate(series):
        if s != initial_s:
            rtf = i
            if i == len(series)-1:
                # If termination occurs at last entry it is not possible
                # to determine the cause of termination (note this should be
                # a low probability event)
                termination_condition = 'unknown'
            elif series[i+1] == s:
                termination_condition = 'double event'
            elif series[i+1] != s:
                termination_condition = 'single event'
            break
    if only_count_min_1:
        if initial_s == 1:
            rtf = 1
    if rtf == len(series) + 1:
        print('Warning did not find a termination event')
    if return_termination_condition:
        return rtf, termination_condition
    else:
        return rtf


def count_rounds_since_flip(series):
    '''
    Used to extract number of consecutive elements that are identical

    input:
        series : array or list
    output:
        rounds_since_change: list
    '''
    round_since_last_change = 0  # start at zero because
    last_s = series[0]
    rounds_since_change = []
    for i, s in enumerate(series):
        if s == last_s:
            round_since_last_change += 1
        else:
            rounds_since_change.append(round_since_last_change)
            round_since_last_change = 1
        last_s = s
    return rounds_since_change


def count_rounds_since_flip_split(series):
    '''
    Used to extract rounds since flip in a binary sequence flipping between
    +1 and -1.

    input:
        series : array or list containing entries +1 and -1
    output:
        rounds_between_flips_m_to_p : list of consecutive entries in +1
        rounds_between_flips_p_to_m : list of consecutive entries in -1
    '''
    nr_rounds_since_last_flip = 1
    last_s = +1
    rounds_between_flips_p_to_m = []
    rounds_between_flips_m_to_p = []
    for i, s in enumerate(series):

        if s == last_s:
            nr_rounds_since_last_flip += 1
        else:
            if s == +1:
                rounds_between_flips_m_to_p.append(nr_rounds_since_last_flip)
            elif s == -1:
                rounds_between_flips_p_to_m.append(nr_rounds_since_last_flip)
            else:
                raise ValueError('Unexpected value in series,' +
                                 ' expect only +1 and -1')
            nr_rounds_since_last_flip = 1
        last_s = s
    return rounds_between_flips_m_to_p, rounds_between_flips_p_to_m


def binary_derivative(series):
    '''
    Used to extract transitions between flipping and non-flipping
    part of data traces.
    '''
    d_series = np.array([1 if series[i+1] == series[i] else -1
                        for i in range(len(series)-1)])
    return d_series


def binary_derivative_2D(data_array, axis=0):
    '''
    Used to extract transitions between flipping and non-flipping
    part of data traces along a certain axis
    '''
    if axis == 0:
        dd_array = np.array([binary_derivative(line)
                            for line in data_array])
    elif axis == 1:
        dd_array = np.array([binary_derivative(line)
                            for line in data_array.T]).T
    return dd_array


def butterfly_data_binning(Z, initial_state=0):
    if initial_state == 0:  # measurement induced excitation
        eps0_0 = np.mean([1 if s == 1 else 0 for s in Z[:, 0]])
        # first is declared second is input state
        eps1_0 = 1-eps0_0
        P00_0 = np.mean([1 if (s_row[:2] == [1., 1.]).all() else 0
                         for s_row in Z[:]])
        P01_0 = np.mean([1 if (s_row[:2] == [1., -1.]).all() else 0
                         for s_row in Z[:]])
        P10_0 = np.mean([1 if (s_row[:2] == [-1., 1.]).all() else 0
                         for s_row in Z[:]])
        P11_0 = np.mean([1 if (s_row[:2] == [-1., -1.]).all() else 0
                         for s_row in Z[:]])
        return {'eps0_0': eps0_0, 'eps1_0': eps1_0, 'P00_0': P00_0,
                'P01_0': P01_0, 'P10_0': P10_0, 'P11_0': P11_0}
    else:  # measurement induced relaxation
        eps0_1 = np.mean([1 if s == 1 else 0 for s in Z[:, 0]])
        # first is declared second is input state
        eps1_1 = 1-eps0_1
        P00_1 = np.mean([1 if (s_row[:2] == [1., 1.]).all() else 0
                         for s_row in Z[:]])
        P01_1 = np.mean([1 if (s_row[:2] == [1., -1.]).all() else 0
                         for s_row in Z[:]])
        P10_1 = np.mean([1 if (s_row[:2] == [-1., 1.]).all() else 0
                         for s_row in Z[:]])
        P11_1 = np.mean([1 if (s_row[:2] == [-1., -1.]).all() else 0
                         for s_row in Z[:]])
        return {'eps0_1': eps0_1, 'eps1_1': eps1_1, 'P00_1': P00_1,
                'P01_1': P01_1, 'P10_1': P10_1, 'P11_1': P11_1}


def butterfly_matrix_inversion(exc_coeffs, rel_coeffs):

    rel_coeffs.update(exc_coeffs)
    coeffs = rel_coeffs
    matr = [[coeffs['eps0_0'], coeffs['eps0_1']],
            [coeffs['eps1_0'], coeffs['eps1_1']]]
    inv_matr = np.linalg.inv(matr)
    P_vec = [coeffs['P00_0'], coeffs['P01_0']]
    eps_vec = np.dot(inv_matr, P_vec)
    [eps00_0, eps01_0] = eps_vec

    P_vec = [coeffs['P10_0'], coeffs['P11_0']]
    eps_vec = np.dot(inv_matr, P_vec)
    [eps10_0, eps11_0] = eps_vec

    matr = [[coeffs['eps0_1'], coeffs['eps0_0']],
            [coeffs['eps1_1'], coeffs['eps1_0']]]
    inv_matr = np.linalg.inv(matr)
    P_vec = [coeffs['P00_1'], coeffs['P01_1']]
    eps_vec = np.dot(inv_matr, P_vec)
    [eps01_1, eps00_1] = eps_vec

    P_vec = [coeffs['P10_1'], coeffs['P11_1']]
    eps_vec = np.dot(inv_matr, P_vec)
    [eps11_1, eps10_1] = eps_vec
    print(coeffs)
    print("eps00_0", eps00_0)
    print("eps01_0", eps01_0)
    print("eps10_0", eps10_0)
    print("eps11_0", eps11_0)
    print("eps00_1", eps00_1)
    print("eps01_1", eps01_1)
    print("eps10_1", eps10_1)
    print("eps11_1", eps11_1)
    return {'eps00_0': eps00_0, 'eps01_0': eps01_0, 'eps10_0': eps10_0,
            'eps11_0': eps11_0, 'eps00_1': eps00_1, 'eps01_1': eps01_1,
            'eps10_1': eps10_1, 'eps11_1': eps11_1}


def digitize(data, threshold, positive_case=True):
    '''
    this funciton digitizes 2D arrays. When using postselection,
    first postselect if threshold for postslection is
    conservative than the threshold for digitization.

    '''
    if positive_case:
        data_digitized = np.asarray([[1 if d_element <= threshold else -1
                                    for d_element in d_row] for d_row in data])
    else:
        data_digitized = np.asarray([[1 if d_element >= threshold else -1
                                    for d_element in d_row] for d_row in data])
    return data_digitized


def postselect(data, threshold, positive_case=True):
    data_postselected = []
    if positive_case:
        for data_row in data:
            if data_row[0] <= threshold:
                data_postselected.append(data_row)
    else:
        for data_row in data:
            if data_row[0] >= threshold:
                data_postselected.append(data_row)
    return np.asarray(data_postselected)


def count_error_fractions(trace):
    '''
    The counters produce the same results as the CBox counters in
    CBox.get_qubit_state_log_counters().
    Requires a boolean array or an array of ints as input.
    '''
    no_err_counter = 0
    single_err_counter = 0
    double_err_counter = 0
    zero_counter = 0
    one_counter = 0

    for i in range(len(trace)):
        if i < (len(trace)-1):
            if trace[i] == trace[i+1]:
                # A single error is associated with a qubit error
                single_err_counter += 1
                if i < (len(trace)-2):
                    if trace[i] == trace[i+2]:
                        # If there are two errors in a row this is associated with
                        # a RO error, this counter must be substracted from the
                        # single counter
                        double_err_counter += 1
            else:
                no_err_counter +=1
        if trace[i] == 1:
            zero_counter +=1
        else:
            one_counter +=1

    return no_err_counter, single_err_counter, double_err_counter, zero_counter, one_counter


def bin_2D_shots(I_shots, Q_shots, normed=True):
    '''
    Creates a 2D histogram of I and Q shotsdata.

    Watch out that when you plot the histogram uses the convention
    H[xbins, ybins] and plotting generally uses H[yrows, xcols] meaning you
    want to Transpose the data using H.T
    '''
    n_bins_range = 60  # the bins we want to have around our data
    V_range_I = np.max(I_shots)-np.min(I_shots)             # data voltagerange
    V_range_Q = np.max(Q_shots)-np.min(Q_shots)

    V_max = np.max([V_range_I, V_range_Q])*1.1

    # determining the amount of bins
    n_bins_range = 60  # the bins we want to have around our data
    V_range = np.max([V_range_I, V_range_Q, V_range_I, V_range_Q])
    n_bins = n_bins_range*2*V_max/V_range

    H, xedges, yedges = np.histogram2d(I_shots, Q_shots,
                                       bins=n_bins,
                                       range=[[-V_max, V_max],
                                              [-V_max, V_max]],
                                       normed=normed)
    return H, xedges, yedges
