import numpy as np

from sagea.pysrc.auxiliary.Preference import Dimension, LoveNumberType
from sagea.pysrc.auxiliary.Preference import GeoConstants
from sagea.pysrc.auxiliary.LoveNumber import LoveNumber


class ConvertSHCConfig:
    def __init__(self):
        self.ln = None

        self.input_field_type = Dimension.Geopotential
        self.output_field_type = Dimension.EWH

    def set_input_type(self, field_type: Dimension):
        self.input_field_type = field_type
        return self

    def set_output_type(self, field_type: Dimension):
        self.output_field_type = field_type
        return self

    def set_Love_number(self, ln):
        self.ln = ln
        return self


class ConvertSHC:
    def __init__(self):
        self.configuration = ConvertSHCConfig()

    def config(self, config: ConvertSHCConfig):
        self.configuration = config
        return self

    def apply_to(self, cs1d):

        length_of_cs1d = np.shape(cs1d)[-1]
        lmax = int(np.sqrt(length_of_cs1d) - 1)

        convert_array = self._get_convert_array_to_dimensionless(
            self.configuration.input_field_type,
            lmax
        ) * self._get_convert_array_from_dimensionless_to(
            self.configuration.output_field_type, lmax
        )
        # [k1, k2, ...,]

        convert_weight_cs1d = np.array([])
        for i in range(lmax + 1):
            convert_weight_cs1d = np.concatenate([convert_weight_cs1d, [convert_array[i]] * (2 * i + 1)])

        cs1d_converted = cs1d * convert_weight_cs1d

        return cs1d_converted

    def _get_convert_array_to_dimensionless(self, field_type: Dimension, lmax):
        """
        return: [k1, k2, ..., kl, ...]
        """
        assert self.configuration.ln is not None
        ln = self.configuration.ln

        convert_mat = np.ones((lmax + 1,))

        density_water = GeoConstants.density_water
        density_earth = GeoConstants.density_earth
        radius_e = GeoConstants.radius_earth
        GM = GeoConstants.GM
        g_wmo = GeoConstants.g_wmo

        if field_type is Dimension.Geopotential:
            pass

        elif field_type is Dimension.EWH:
            ln = ln[:lmax + 1]
            kl = np.array([(1 + ln[n]) / (2 * n + 1) for n in range(len(ln))]) * 3 * density_water / (
                    radius_e * density_earth)

            convert_mat *= kl

        elif field_type is Dimension.Density:
            ln = ln[:lmax + 1]
            kl = np.array([(1 + ln[n]) / (2 * n + 1) for n in range(len(ln))]) * 3 / (radius_e * density_earth)

            convert_mat *= kl

        elif field_type is Dimension.Geoid:
            convert_mat /= radius_e

        elif field_type is Dimension.Gravity:
            kl = np.array([n - 1 for n in range(lmax + 1)]) * (GM / radius_e ** 2)
            convert_mat /= kl

        elif field_type is Dimension.VerticalDisplacement:
            lnh, lnl = self.__get_love_number_h_and_l(lmax)

            ln = ln[:lmax + 1]
            kl = np.array([lnh[n] / (1 + ln[n]) for n in range(len(ln))]) * radius_e

            convert_mat /= kl

        elif field_type is Dimension.Pressure:
            termI = np.arange(lmax + 1)
            term = 2 * termI + 1.
            ln = ln[:lmax + 1]

            kl = (radius_e * density_earth / 3) * (term / (1 + ln)) * g_wmo

            convert_mat /= kl

        else:
            raise Exception

        return convert_mat

    def _get_convert_array_from_dimensionless_to(self, field_type: Dimension, lmax):
        """
        return: [k1, k2, ..., kl, ...]
        """

        assert self.configuration.ln is not None
        ln = self.configuration.ln

        density_water = GeoConstants.density_water
        density_earth = GeoConstants.density_earth
        radius_e = GeoConstants.radius_earth
        GM = GeoConstants.GM
        g_wmo = GeoConstants.g_wmo

        convert_mat = np.ones((lmax + 1,))

        if field_type is Dimension.Geopotential:
            pass

        elif field_type is Dimension.EWH:
            ln = ln[:lmax + 1]
            kl = np.array([(2 * n + 1) / (1 + ln[n]) for n in range(len(ln))]) * radius_e * density_earth / (
                    3 * density_water)

            convert_mat *= kl

        elif field_type is Dimension.Density:
            ln = ln[:lmax + 1]
            kl = np.array([(2 * n + 1) / (1 + ln[n]) for n in range(len(ln))]) * radius_e * density_earth / 3

            convert_mat *= kl

        elif field_type is Dimension.Geoid:
            convert_mat *= radius_e

        elif field_type is Dimension.Gravity:
            kl = np.array([n - 1 for n in range(lmax + 1)]) * (GM / radius_e ** 2)
            convert_mat *= kl

        elif field_type is Dimension.VerticalDisplacement:
            lnh, lnl = self.__get_love_number_h_and_l(lmax)

            ln = ln[:lmax + 1]
            kl = np.array([(lnh[n] / (1 + ln[n])) for n in range(len(ln))]) * radius_e

            convert_mat *= kl

        elif field_type is Dimension.Pressure:
            termI = np.arange(lmax + 1)
            term = 2 * termI + 1.
            ln = ln[:lmax + 1]

            kl = (radius_e * density_earth / 3) * (term / (1 + ln)) * g_wmo

            convert_mat *= kl

        elif field_type in (
                Dimension.HorizontalDisplacementNorth, Dimension.HorizontalDisplacementEast):
            lnh, lnl = self.__get_love_number_h_and_l(lmax)

            ln = ln[:lmax + 1]
            kl = np.array([lnl[n] / (1 + ln[n]) for n in range(len(ln))]) * radius_e

            convert_mat *= kl

        else:
            raise Exception

        return convert_mat

    @staticmethod
    def __get_love_number_h_and_l(lmax):
        LN = LoveNumber()

        LN.configuration.set_lmax(lmax).set_type(LoveNumberType.VerticalDisplacement)  # h
        ln_h = LN.get_Love_number()

        LN.configuration.set_lmax(lmax).set_type(LoveNumberType.HorizontalDisplacement)  # l
        ln_l = LN.get_Love_number()

        return ln_h, ln_l
