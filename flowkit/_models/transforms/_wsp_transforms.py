"""
Transform classes compatible with FlowJo 10
"""
import os
import numpy as np
from scipy import interpolate
from ._base_transform import Transform
from ..._resources import resource_path

BIEX_NEG_VALUES = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
BIEX_WIDTH_VALUES = [
    -1000.,
    -630.957336,
    -501.187225,
    -398.107178,
    -316.227753,
    -251.188644,
    -158.489319,
    -100.,
    -63.095734,
    -39.810719,
    -25.118864,
    -15.848932,
    -10.,
    -7.943282,
    -6.309574,
    -5.011872,
    -3.981072,
    -3.162278,
    -2.511886,
    -1.584893,
    -1.
]


class WSPLogTransform(Transform):
    """
    Logarithmic transform as implemented in FlowJo 10.

    :param transform_id: A string identifying the transform
    :param offset: A positive number used to offset event data
    :param decades: A positive number of for the desired number of decades
    """
    def __init__(
        self,
        transform_id,
        offset,
        decades
    ):
        Transform.__init__(self, transform_id)

        self.offset = offset
        self.decades = decades

    def __repr__(self):
        return (
            f'{self.__class__.__name__}('
            f'{self.id}, offset: {self.offset}, decades: {self.decades})'
        )

    def apply(self, events):
        """
        Apply transform to given events.

        :param events: NumPy array of FCS event data
        :return: NumPy array of transformed events
        """
        new_events = np.copy(events)
        new_events[new_events < self.offset] = self.offset
        new_events = 1. / self.decades * (np.log10(new_events) - np.log10(self.offset))

        return new_events


class WSPBiexTransform(Transform):
    """
    Biex transform as implemented in FlowJo 10. This transform is applied exactly as
    the FlowJo 10 is implemented, using lookup tables with only a limited set
    of parameter values. See the supported values in the BIEX_NEG_VALUES and
    BIEX_WIDTH_VALUES arrays within the `transforms` module.

    :param transform_id: A string identifying the transform
    :param negative: Value for the FlowJo biex option 'negative' (float)
    :param width: Value for the FlowJo biex option 'width' (float)
    :param use_nearest: Given unsupported negative and width values, choose the
        nearest supported value. Default is False
    """
    def __init__(
        self,
        transform_id,
        negative=0,
        width=-10,
        use_nearest=False
    ):
        Transform.__init__(self, transform_id)

        self.negative = negative
        self.width = width

        if use_nearest:
            self.negative = min(BIEX_NEG_VALUES, key=lambda neg_x: abs(neg_x - negative))

        if self.width not in BIEX_WIDTH_VALUES:
            closest_width1 = min(BIEX_WIDTH_VALUES, key=lambda width_x: abs(width_x - width))
            new_width_list = [w for w in BIEX_WIDTH_VALUES if w != closest_width1]
            closest_width2 = min(new_width_list, key=lambda width_x2: abs(width_x2 - width))

            lut_file_name1 = "tr_biex_l256_w%.6f_n%.6f_m4.418540_r262144.000029.csv" % (closest_width1, self.negative)
            lut_file_path1 = os.path.join(resource_path, 'flowjo_xforms', lut_file_name1)

            lut_file_name2 = "tr_biex_l256_w%.6f_n%.6f_m4.418540_r262144.000029.csv" % (closest_width2, self.negative)
            lut_file_path2 = os.path.join(resource_path, 'flowjo_xforms', lut_file_name2)

            y1, x1 = np.loadtxt(lut_file_path1, delimiter=',', usecols=(0, 1), skiprows=1, unpack=True)
            y2, x2 = np.loadtxt(lut_file_path2, delimiter=',', usecols=(0, 1), skiprows=1, unpack=True)

            # Now calculate the weights. We want higher weights for closer values,
            # which can be calculated by just flipping the relative distances.
            # since we want higher weights for closer values
            diff_width = abs(closest_width1 - closest_width2)
            weight1 = 1. - (abs(closest_width1 - width) / diff_width)
            weight2 = 1. - (abs(closest_width2 - width) / diff_width)

            x = np.average([x1, x2], weights=[weight1, weight2], axis=0)
            y = y1
        else:
            lut_file_name = "tr_biex_l256_w%.6f_n%.6f_m4.418540_r262144.000029.csv" % (self.width, self.negative)
            lut_file_path = os.path.join(resource_path, 'flowjo_xforms', lut_file_name)

            # the LUT files have the transformed value in the 1st column
            try:
                y, x = np.loadtxt(lut_file_path, delimiter=',', usecols=(0, 1), skiprows=1, unpack=True)
            except OSError:
                raise ValueError(
                    "The parameter value combination negative=%f, width=%f is unsupported" % (self.negative, self.width)
                )

        # create interpolation function with any values outside the range set to the min / max of LUT
        self._lut_func = interpolate.interp1d(x, y, kind='linear', bounds_error=False, fill_value=(y.min(), y.max()))

    def __repr__(self):
        return (
            f'{self.__class__.__name__}('
            f'{self.id}, width: {self.width}, neg: {self.negative})'
        )

    def apply(self, events):
        """
        Apply transform to given events.

        :param events: NumPy array of FCS event data
        :return: NumPy array of transformed events
        """
        new_events = self._lut_func(events)

        return new_events
