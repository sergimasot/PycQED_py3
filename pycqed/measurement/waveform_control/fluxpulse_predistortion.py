import numpy as np
import scipy.signal as signal

def import_iir(filename):
    '''
    imports csv files generated with Mathematica notebooks of the form
    a1_0,b0_0,b1_0
    a1_1,b0_1,b1_1
    a1_2,b0_2,b1_2
    .
    .
    .

    args:
        filename : string containging to full path of the file (or only the filename if in same directory)

    returns:
        [aIIRfilterLis,bIIRfilterList] : list of two numpy arrays compatable for use
        with the scipy.signal.lfilter() function
        used by filterIIR() function

    '''
    IIRfilterList = np.loadtxt(filename,
                               delimiter=',')
    aIIRfilterList = np.transpose(np.vstack((np.ones(len(IIRfilterList)),
                                             -IIRfilterList[:,0])))
    bIIRfilterList = IIRfilterList[:,1:]

    return [aIIRfilterList,bIIRfilterList]


def filter_fir(kernel,x):
    '''
    function to apply a FIR filter to a dataset

    args:
        kernel: FIR filter kernel
        x:      data set
    return:
        y :     data convoluted with kernel, aligned such that pulses do not
                shift (expects kernel to have a impulse like peak)
    '''
    iMax = kernel.argmax()
    y = np.convolve(x,kernel,mode='full')[iMax:(len(x)+iMax)]
    return y


def filter_iir(aIIRfilterList,bIIRfilterList,x):
    '''
    applies IIR filter to the data x (aIIRfilterList and bIIRfilterList are load by the importIIR() function)

    args:
        aIIRfilterList : array containing the a coefficients of the IIR filters
                         (one row per IIR filter with coefficients 1,-a1,-a2,.. in the form required by scipy.signal.lfilter)
        bIIRfilterList : array containing the b coefficients of the IIR filters
                         (one row per IIR filter with coefficients b0, b1, b2,.. in the form required by scipy.signal.lfilter)
        x : data array to be filtered

    returns:
        y : filtered data array
    '''
    y = x
    for a,b in zip(aIIRfilterList,bIIRfilterList):
        y = signal.lfilter(b,a,y)
    return y




def distort_qudev(element, distortion_dict):
    """
    Distorts an element using the contenst of a distortion dictionary.
    The distortion dictionary should be formatted as follows.

    distortion_dict = {'ch_list': ['chx', 'chy', ...],
              'chx': filter_dict,
              'chy': filter_dict,
              ...
              }
    with filter_dict = {'FIR' : filter_fernel, 'IIR':  [aIIRfilterLis,bIIRfilterList]}

    args:
        element : element instance of the Element class in element.py module
        distortion_dict : distortion dictionary (format see above)

    returns : element with distorted waveforms attached (element.distorted_wfs)
    """
    t_vals, wfs_dict = element.waveforms()
    for ch in distortion_dict['ch_list']:
        element.chan_distorted[ch] = True
        kernelvec = distortion_dict[ch]['FIR']
        wf_dist = wfs_dict[ch]
        if kernelvec is not None:
            wf_dist = filter_fir(kernelvec,wfs_dict[ch])
        if distortion_dict[ch]['IIR'] is not None:
            aIIRfilterList,bIIRfilterList = distortion_dict[ch]['IIR']
            wf_dist = filter_iir(aIIRfilterList,bIIRfilterList,wf_dist)
        element.distorted_wfs[ch] = wf_dist
    return element








