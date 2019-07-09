# A Sequence contains segments which then contain the pulses. The Sequence
# provides the information for the AWGs, in which order to play the segments.
#
# author: Michael Kerschbaum
# created: 04/2019

import numpy as np
from copy import deepcopy
import pycqed.measurement.waveform_control.pulse_library as pl
import pycqed.measurement.waveform_control.pulse as bpl  # base pulse lib
import pycqed.measurement.waveform_control.pulsar as ps
import pycqed.measurement.waveform_control.segment as sg
from collections import OrderedDict as odict


class Sequence:
    """
    A Sequence consists of several segments, which can be played back on the 
    AWGs sequentially.
    """

    def __init__(self, name):
        self.name = name
        self.pulsar = ps.Pulsar.get_instance()
        self.segments = odict()
        self.awg_sequence = {}

    def add(self, segment):
        if segment.name in self.segments:
            raise Exception('Name {} already exisits in the sequence!'.format(
                segment.name))
        self.segments[segment.name] = segment

    def sequence_for_awg(self):
        """
        Stores the for all AWGs the sequence of elements in self.sequence_for_awg.
        """

        self.awg_sequence = {}
        for awg in self.pulsar.awgs:
            self.awg_sequence[awg] = []
            for segment in self.segments:
                seg = self.segments[segment]
                seg.gen_elements_on_awg()

                if awg not in seg.elements_on_awg:
                    continue

                for element in seg.elements_on_awg[awg]:
                    self.awg_sequence[awg].append([element, segment])
                    if element in seg.acquisition_elements:
                        self.awg_sequence[awg][-1].append('RO')
