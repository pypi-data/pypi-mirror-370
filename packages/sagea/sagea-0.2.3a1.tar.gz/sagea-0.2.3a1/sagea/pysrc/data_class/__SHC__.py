#!/use/bin/env python
# coding=utf-8
# @Author  : Shuhao Liu
# @Time    : 2025/6/13 10:34 
# @File    : __SHC__.py
import copy
import warnings

import numpy as np

from sagea.pysrc.auxiliary.Preference import GeoConstants, SHNormalization, Dimension
import sagea.pysrc.auxiliary.Preference as Enums
from sagea.pysrc.auxiliary.TimeTool import TimeTool
from sagea.pysrc.auxiliary.MathTool import MathTool
from sagea.pysrc.post_processing.filter.GetSHCFilter import get_filter
from sagea.pysrc.auxiliary import Preference
from sagea.pysrc.auxiliary.LoveNumber import LoveNumber
from sagea.pysrc.post_processing.convert_field_physical_quantity.ConvertSHC import ConvertSHC
from sagea.pysrc.post_processing.geometric_correction.GeometricalCorrection import GeometricalCorrection
from sagea.pysrc.post_processing.harmonic.Harmonic import Harmonic


class SHC:
    """
    This class is to store the spherical harmonic coefficients (SHCs) for the use in necessary data processing.

    Attribute self.value stores the coefficients in 2d-array (in numpy.ndarray) combined with c and s.
    which are sorted by degree, for example,
    numpy.ndarray: [[c1[0,0]; s1[1,1], c1[1,0], c1[1,1]; s1[2,2], s1[2,1], c1[2,0], c1[2,1], c1[2,2]; ...],
     [c2[0,0]; s2[1,1], c2[1,0], c2[1,1]; s2[2,2], s2[2,1], c2[2,0], c2[2,1], c2[2,2]; ...],
     [                                        ...                                         ]].
    Note that even it stores only one set of SHCs, the array is still 2-dimension, i.e.,
    [[c1[0,0]; s1[1,1], c1[1,0], c1[1,1]; s1[2,2], s1[2,1], c1[2,0], c1[2,1], c1[2,2]; ...]].

    Attribute self.normalization indicates the normalization of the SHCs (in sagea.Preference.SHNormalization), for example,
    sagea.Preference.SHNormalization.full.

    Attribute self.physical_dimension indicates the physical dimension of the SHCs (in sagea.Preference.PhysicalDimensions).
    """

    def __init__(self, c, s=None, normalization=None, dimension: Preference.Dimension = None):
        """

        :param c:
                if s is not None:
                    harmonic coefficients c in 2-dimension (l,m), or a series (q,l,m);
                else:
                    1-dimension array sorted by degree [c00, s11, c10, c11, s22, s21, ...]
                    or 1-dimension array sorted by degree [[c00, s11, c10, c11, s22, s21, ...],[...]]

        :param s: harmonic coefficients s in 2-dimension (l,m), or a series (q,l,m),
                or None.

        :param normalization: in Preference.SHNormalization, defaults to .full.

        :param dimension: in Preference.PhysicalDimensions, defaults to .Dimensionless.
        """
        if s is None:
            self.value = np.array(c)
            if len(self.value.shape) == 1:
                self.value = np.array([self.value])

        else:
            assert np.shape(c) == np.shape(s)

            if len(np.shape(c)) == 2:
                self.value = MathTool.cs_combine_to_triangle_1d(c, s)

            elif len(np.shape(c)) == 3:
                cs = []
                for i in range(np.shape(c)[0]):
                    this_cs = MathTool.cs_combine_to_triangle_1d(c[i], s[i])
                    cs.append(this_cs)
                self.value = np.array(cs)

        if len(np.shape(self.value)) == 1:
            self.value = self.value[None, :]

        assert len(np.shape(self.value)) == 2

        if normalization is None:
            normalization = Preference.SHNormalization.full
        assert normalization in Preference.SHNormalization
        self.__normalization = normalization

        if dimension is None:
            dimension = Preference.Dimension.Dimensionless
        assert dimension in Preference.Dimension

        self.__dimension = dimension

    def append(self, *params):
        """

        :param params: One parameter of instantiated SHC,
         or two parameters of c and s with the same input requirement as SHC.
        :return: self
        """
        assert len(params) in (1, 2)

        if len(params) == 1:
            if issubclass(type(params[0]), SHC):
                shc = params[0]
            else:
                shc = SHC(params[0])

        else:
            shc = SHC(*params)

        assert np.shape(shc.value)[-1] == np.shape(self.value)[-1]

        self.value = np.concatenate([self.value, shc.value])

        return self

    def is_series(self):
        """
        To determine whether the spherical harmonic coefficients stored in this class are one group or multiple groups.
        :return: bool, True if it stores multiple groups, False if it stores only one group.
        """
        return self.get_length() != 1

    def get_length(self):
        """
        To get the number of sets.
        """
        return np.shape(self.value)[0]

    def __len__(self):
        return self.get_length()

    def __getitem__(self, idx):
        assert type(idx) in (int, slice, str)

        if type(idx) in (int, slice):
            return self.__getitem_index_q(idx)
        elif type(idx) in (str,):
            return self.__getitem_index_cs(idx)
        else:
            assert False

    def __getitem_index_q(self, idx: int or slice):
        if type(idx) is int:
            assert 0 <= idx < len(self)
            idx = slice(idx, idx + 1)
        elif type(idx) is slice:
            assert idx.start >= 0
            assert idx.stop is None or idx.stop < len(self)
        else:
            assert False

        sliced_value = self.value[idx]

        return SHC(sliced_value, normalization=self.__normalization, dimension=self.__dimension)

    def __getitem_index_cs(self, idx: str):
        if type(idx) is str:
            cs1d_idx = MathTool.get_cs_1d_index(idx)
            return self.value[:, cs1d_idx]

        else:
            assert False

    def __setitem__(self, idx, value):
        assert type(idx) in (int, slice, str)

        if type(idx) in (int, slice):
            return self.__setitem_index_q(idx, value)
        elif type(idx) in (str,):
            return self.__setitem_index_cs(idx, value)
        else:
            assert False

    def __setitem_index_q(self, idx: int or slice, value):
        if type(idx) is int:
            assert 0 <= idx < len(self)
            idx = slice(idx, idx + 1)
        elif type(idx) is slice:
            assert idx.start >= 0
            assert idx.stop is None or idx.stop < len(self)
        else:
            assert False
        assert len(self[idx]) == len(value)

        assert type(value) is SHC
        assert self.get_lmax() == value.get_lmax()

        if self.__dimension != value.get_dimension():
            warnings.warn("set with SHC of different dimension")

        self.value[idx] = value.value
        return self

    def __setitem_index_cs(self, idx: int or slice, value):
        if type(idx) is str:
            cs1d_idx = MathTool.get_cs_1d_index(idx)

            if MathTool.is_number(value):
                value = np.array([float(value)] * len(self))

            assert np.shape(value) == (len(self),)

            self.value[:, cs1d_idx] = value

        else:
            assert False

    def get_lmax(self):
        """

        :return: int, max degree/order of the spherical harmonic coefficients stored in this class.
        """
        length_of_cs1d = np.shape(self.value)[-1]
        lmax = int(np.sqrt(length_of_cs1d) - 1)

        return lmax

    def get_dimension(self):
        """

        :return:
        """

        return self.__dimension

    def set_dimension(self, physical_dimension: Dimension):
        self.__dimension = physical_dimension

        return self

    def get_normalization(self):
        """

        :return:
        """

        return self.__normalization

    def set_normalization(self, normalization: SHNormalization):
        self.__normalization = normalization
        return self

    def get_cs2d(self, fill_value=0):
        """
        return: cqlm, sqlm. Both cqlm and sqlm are 3-dimension, EVEN IF NOT self.is_series()
        """
        lmax = self.get_lmax()

        num_of_series = np.shape(self.value)[0]

        cqlm = np.zeros((num_of_series, lmax + 1, lmax + 1))
        sqlm = np.zeros((num_of_series, lmax + 1, lmax + 1))

        for i in range(num_of_series):
            this_cs = self.value[i]
            this_clm, this_slm = MathTool.cs_decompose_triangle1d_to_cs2d(this_cs)
            cqlm[i, :, :] = this_clm
            sqlm[i, :, :] = this_slm

        return cqlm, sqlm

    def __de_average(self):
        if self.is_series():
            self.value -= np.mean(self.value, axis=0)
        else:
            raise Exception

    def get_average(self):
        return SHC(np.mean(self.value, axis=0))

    def de_background(self, background=None):
        """
        if background is None, de average
        """
        if background is None:
            self.__de_average()

        else:
            assert isinstance(background, SHC)
            assert not background.is_series()

            self.value -= background.value

    @staticmethod
    def identity(lmax: int):
        basis_num = (lmax + 1) ** 2
        cs = np.eye(basis_num)

        return SHC(cs)

    def __add__(self, other):
        assert isinstance(other, SHC)
        assert self.get_lmax() == other.get_lmax()
        if self.get_dimension() != other.get_dimension():
            warnings.warn("add between different dimensions")

        self.value += other.value
        return self

    def __sub__(self, other):
        assert isinstance(other, SHC)
        assert self.get_lmax() == other.get_lmax()
        if self.get_dimension() != other.get_dimension():
            warnings.warn("subtract between different dimensions")

        self.value -= other.value
        return self

    def add(self, shc, lbegin=None, lend=None):
        if (lend is None) and (lbegin is None):
            self.value += shc.value
            return self

        else:
            assert (lend is None) or (0 <= lend <= self.get_lmax())
            assert (lbegin is None) or (0 <= lbegin <= self.get_lmax())

            shc_copy = copy.deepcopy(shc)

            if lend is not None:
                shc_copy.value[:, (lend + 1) ** 2:] = 0
            if lbegin is not None:
                shc_copy.value[:, :lbegin ** 2] = 0

            return self.add(shc_copy)

    def subtract(self, shc, lbegin=None, lend=None):
        if (lend is None) and (lbegin is None):
            self.value -= shc.value
            return self

        else:
            assert (lend is None) or (0 <= lend <= self.get_lmax())
            assert (lbegin is None) or (0 <= lbegin <= self.get_lmax())

            shc_copy = copy.deepcopy(shc)

            if lend is not None:
                shc_copy.value[:, (lend + 1) ** 2:] = 0
            if lbegin is not None:
                shc_copy.value[:, :lbegin ** 2] = 0

            return self.subtract(shc_copy)

    def get_degree_rms(self):
        cqlm, sqlm = self.get_cs2d()
        return MathTool.cs_get_degree_rms(cqlm, sqlm)

    def get_degree_rss(self):
        cqlm, sqlm = self.get_cs2d()
        return MathTool.cs_get_degree_rss(cqlm, sqlm)

    def get_cumulative_degree_rss(self):
        cqlm, sqlm = self.get_cs2d()
        return MathTool.cs_get_cumulative_degree_rss(cqlm, sqlm)

    def get_std(self):
        cs_std = np.std(self.value, axis=0)
        return SHC(cs_std)

    def convert_type(self, to_type: Preference.Dimension, from_type: Preference.Dimension = None):
        from_type = self.__dimension if from_type is None else from_type

        assert from_type in Preference.Dimension
        assert from_type.value <= 99, f"from_type should be a physical dimension, got {from_type} instead."

        assert to_type in Preference.Dimension
        assert to_type.value <= 99, f"to_type should be a physical dimension, got {from_type} instead."

        lmax = self.get_lmax()
        LN = LoveNumber()
        LN.configuration.set_lmax(lmax)

        ln = LN.get_Love_number()

        convert = ConvertSHC()
        convert.configuration.set_Love_number(ln).set_input_type(from_type).set_output_type(to_type)

        self.value = convert.apply_to(self.value)
        self.__dimension = to_type
        return self

    def filter(self, method: Preference.SHCFilterType or Preference.SHCDecorrelationType, param: tuple = None):
        assert method in Enums.SHCFilterType or method in Preference.SHCDecorrelationType
        cqlm, sqlm = self.get_cs2d()
        filtering = get_filter(method, param, lmax=self.get_lmax())
        cqlm_f, sqlm_f = filtering.apply_to(cqlm, sqlm)
        self.value = MathTool.cs_combine_to_triangle_1d(cqlm_f, sqlm_f)

        return self

    def to_GRD(self, grid_space=None):
        from sagea.pysrc.data_class.__GRD__ import GRD

        """pure synthesis"""

        if grid_space is None:
            grid_space = int(180 / self.get_lmax())

        lat, lon = MathTool.get_global_lat_lon_range(grid_space)

        lmax = self.get_lmax()
        har = Harmonic(lat, lon, lmax, option=1)

        cqlm, sqlm = self.get_cs2d()

        if self.__dimension in (Preference.Dimension.HorizontalDisplacementEast,
                                Preference.Dimension.HorizontalDisplacementNorth):
            grid_data = har.synthesis(cqlm, sqlm, special_type=self.__dimension)

        else:
            grid_data = har.synthesis(cqlm, sqlm)

        grid = GRD(grid_data, lat, lon, option=1, dimension=self.__dimension)
        if grid.get_dimension() == Preference.Dimension.DimensionlessMask:
            grid.limiter(0.5, 1, 0)

        return grid

    def synthesis(self, lat, lon, discrete: bool = False, special_type: Preference.Dimension = None):
        """
        :param lat: numpy.ndarray, latitudes in unit degree
        :param lon: numpy.ndarray, longitudes in unit degree
        :param discrete: bool, if True, the params lat and lon represent each point, and should be of the same length;
            else params lat and lon represent the profiles. Default is False.
        :param special_type: Preference.Dimension, optional.
        """

        lmax = self.get_lmax()
        har = Harmonic(lat, lon, lmax, option=1, discrete=discrete)

        cqlm, sqlm = self.get_cs2d()
        grid_data = har.synthesis(cqlm, sqlm, special_type=special_type)

        return grid_data

    def geometric(self, assumption: Preference.GeometricCorrectionAssumption, log=False):
        gc = GeometricalCorrection()
        cqlm, sqlm = self.get_cs2d()
        cqlm_new, sqlm_new = gc.apply_to(cqlm, sqlm, assumption=assumption, log=log)
        self.value = MathTool.cs_combine_to_triangle_1d(cqlm_new, sqlm_new)

        return self

    def replace(self, index: str, new: np.ndarray):
        """

        :param index: str, like "c2,0" or "s1,1"
        :param new:
        :return:
        """
        assert isinstance(new, SHC) or isinstance(new, np.ndarray)

        index1d = MathTool.get_cs_1d_index(index)

        if isinstance(new, SHC):
            new_array = new.value[:, index1d]
        else:
            new_array = new

        assert len(new_array) == len(self)

        index_new_array_valid = np.where(new_array == new_array)

        self.value[index_new_array_valid, index1d] = new_array[index_new_array_valid]

    def linear_expand(self, time):
        assert not self.is_series()

        year_frac = TimeTool.convert_date_format(time,
                                                 input_type=TimeTool.DateFormat.ClassDate,
                                                 output_type=TimeTool.DateFormat.YearFraction)

        year_frac = np.array(year_frac)

        trend = self.value[0]
        value = year_frac[:, None] @ trend[None, :]
        return SHC(value)

    def regional_extraction(self, shc_region, average=True):
        assert isinstance(shc_region, SHC)

        extraction = (shc_region.value @ self.value.T) * (GeoConstants.radius_earth ** 2)

        if average:
            extraction /= (shc_region.value[:, None, 0] * (GeoConstants.radius_earth ** 2))

        else:
            if self.__normalization == SHNormalization.full:
                extraction *= (4 * np.pi)
            else:
                assert False

        return extraction
