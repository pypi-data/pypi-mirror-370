import copy
import datetime
import pathlib

import h5py
import netCDF4
import numpy as np

import sagea
from sagea.pysrc.auxiliary.MathTool import MathTool
from sagea.pysrc.auxiliary.TimeTool import TimeTool
import sagea.pysrc.auxiliary.Preference as Preference

from sagea.pysrc.post_processing.de_aliasing.DeAliasing import DeAliasing
from sagea.pysrc.post_processing.filter.GetSHCFilter import get_filter
from sagea.pysrc.post_processing.harmonic.Harmonic import Harmonic
from sagea.pysrc.post_processing.leakage.Addictive import Addictive
from sagea.pysrc.post_processing.leakage.BufferZone import BufferZone
from sagea.pysrc.post_processing.leakage.DataDriven import DataDriven
from sagea.pysrc.post_processing.leakage.ForwardModeling import ForwardModeling
from sagea.pysrc.post_processing.leakage.Iterative import Iterative
from sagea.pysrc.post_processing.leakage.Multiplicative import Multiplicative
from sagea.pysrc.post_processing.leakage.Scaling import Scaling
from sagea.pysrc.post_processing.leakage.ScalingGrid import ScalingGrid
from sagea.pysrc.post_processing.seismic_correction.SeismicCorrection import SeismicCorrection


class GRD:
    def __init__(self, value, lat: np.ndarray, lon: np.ndarray, option=1, dimension: Preference.Dimension = None):
        """
        To create a GRD object,
        one needs to specify the data (grid) and corresponding latitude range (lat) and longitude range (lon).
        :param value: 2d- or 3d-array gridded signal, index ([num] ,lat, lon)
        :param lat: co-latitude in [rad] if option=0 else latitude in [degree]
        :param lon: longitude in [rad] if option=0 else longitude in [degree]
        :param option: set 0 if input colat and lon are in [rad]
        :param dimension: in type of sagea.Preference.PhysicalDimension
        """
        if np.ndim(value) == 2:
            value = [value]
        assert np.shape(value)[-2:] == (len(lat), len(lon))

        self.value = np.array(value)
        lat = np.array(lat)
        lon = np.array(lon)

        if option == 0:
            self.lat = 90 - np.degrees(lat)
            self.lon = np.degrees(lon)

        else:
            self.lat = lat
            self.lon = lon

        if dimension is None:
            self.__dimension = Preference.Dimension.Geopotential
        else:
            self.__dimension = dimension

        pass

    def __add__(self, other):
        assert isinstance(other, GRD)
        assert all(other.lat == self.lat) and all(other.lon == self.lon)

        return GRD(self.value + other.value, lat=self.lat, lon=self.lon)

    def __sub__(self, other):
        assert isinstance(other, GRD)
        assert all(other.lat == self.lat) and all(other.lon == self.lon)

        return GRD(self.value - other.value, lat=self.lat, lon=self.lon)

    def get_dimension(self):
        """

        :return:
        """

        return self.__dimension

    def append(self, grid, lat=None, lon=None, option=0):
        """

        :param grid: instantiated GRID or a 2d-array of index (lat, lon).
                        If 2d-array, the lat and lon range should be the same with self.lat and self.lon;
                        If instantiated GRID, params lat, lon and option are not needed.
        :param lat: co-latitude in [rad] if option=0 else latitude in [degree]
        :param lon: longitude in [rad] if option=0 else longitude in [degree]
        :param option:
        :return:
        """
        assert type(grid) in (GRD, np.ndarray)

        if type(grid) is GRD:
            assert lat is None and lon is None
            assert grid.lat == self.lat
            assert grid.lon == self.lon

        else:
            assert np.shape(grid)[-2:] == (len(self.lat), len(self.lon))
            grid = GRD(grid, self.lat, self.lon, option)

        array_to_append = grid.value if grid.is_series() else np.array([grid.value])
        array_self = self.value if self.is_series() else [self.value]

        self.value = np.concatenate([array_self, array_to_append])

        return self

    def is_series(self):
        """
        To determine whether the data stored in this class are one group or multiple groups.
        :return: bool, True if it stores multiple groups, False if it stores only one group.
        """
        return len(self) > 1

    def get_grid_space(self):
        """
        return: grid_space in unit [degree]
        """
        return round(self.lat[1] - self.lat[0], 2)

    def get_length(self):
        return self.value.shape[0]

    def __len__(self):
        return self.get_length()

    def to_SHC(self, lmax=None):
        from sagea.pysrc.data_class.__SHC__ import SHC

        grid_space = self.get_grid_space()

        if self.__dimension in (
                Preference.Dimension.HorizontalDisplacementEast,
                Preference.Dimension.HorizontalDisplacementNorth):
            special_type = self.__dimension
        else:
            special_type = None

        assert special_type in (
            None,
            Preference.Dimension.HorizontalDisplacementEast,
            Preference.Dimension.HorizontalDisplacementNorth,
        )

        if special_type in (
                Preference.Dimension.HorizontalDisplacementEast,
                Preference.Dimension.HorizontalDisplacementNorth):
            assert False, "Horizontal Displacement is not supported yet."

        if lmax is None:
            lmax = int(180 / grid_space)

        lat, lon = MathTool.get_global_lat_lon_range(grid_space)

        har = Harmonic(lat, lon, lmax, option=1)

        grid_data = self.value
        cqlm, sqlm = har.analysis(grid_data, special_type=special_type)

        shc = SHC(cqlm, sqlm, dimension=self.__dimension)

        return shc

    def filter(self, method: Preference.GridFilterType, param: tuple = None):
        assert method in Preference.GridFilterType
        filtering = get_filter(method, param)
        self.value = filtering.apply_to(self.value, option=1)
        return self

    def leakage(self, method: Preference.LeakageMethod, basin: np.ndarray, filter_type, filter_param: tuple, lmax: int,
                # necessary params
                model=None,
                # extra params for model-driven methods
                prefilter_type: Preference.SHCFilterType = Preference.SHCFilterType.Gaussian,
                prefilter_param: tuple = (50,),
                # extra params for iterative
                scale_type: str = "trend", shc_unfiltered=None,
                # extra params for scaling and scaling_grid
                basin_conservation: np.ndarray = None, fm_iter_times: int = 30, log=False
                # extra params for forward modeling
                ):
        assert False, "not implemented"

        assert method in Preference.LeakageMethod
        methods_of_model_driven = (
            Preference.LeakageMethod.Additive, Preference.LeakageMethod.Multiplicative,
            Preference.LeakageMethod.Scaling, Preference.LeakageMethod.ScalingGrid
        )

        methods_of_data_driven = (
            Preference.LeakageMethod.ForwardModeling, Preference.LeakageMethod.DataDriven,
            Preference.LeakageMethod.BufferZone, Preference.LeakageMethod.Iterative
        )

        grid_space = self.get_grid_space()
        lat, lon = MathTool.get_global_lat_lon_range(grid_space)
        har = Harmonic(lat, lon, lmax, option=1)

        if filter_type == Preference.GridFilterType.VGC and len(filter_param) <= 4:
            filter_param = list(filter_param) + [None] * (4 - len(filter_param)) + [har]
            filter_param = tuple(filter_param)

        filtering = get_filter(filter_type, filter_param, lmax=lmax)

        if method in methods_of_model_driven:
            # assert {"time", "model"}.issubset(set(reference.keys()))

            if method == Preference.LeakageMethod.Additive:
                lk = Addictive()

            elif method == Preference.LeakageMethod.Multiplicative:
                lk = Multiplicative()

            elif method == Preference.LeakageMethod.Scaling:
                lk = Scaling()

            elif method == Preference.LeakageMethod.ScalingGrid:
                lk = ScalingGrid()
                lk.configuration.set_scale_type(scale_type)

            else:
                assert False

            if isinstance(model, GRD):
                model = model.value
            lk.configuration.set_model(model)

        elif method in methods_of_data_driven:
            if method == Preference.LeakageMethod.DataDriven:
                assert shc_unfiltered is not None, "Data-driven requires parameter shc_unfiltered."

                lk = DataDriven()
                lk.configuration.set_cs_unfiltered(*shc_unfiltered.get_cs2d())

            elif method == Preference.LeakageMethod.BufferZone:
                lk = BufferZone()

            elif method == Preference.LeakageMethod.ForwardModeling:
                assert basin_conservation is not None, "Forward Modeling requires parameter basin_conservation."
                assert fm_iter_times is not None, "Forward Modeling requires parameter fm_iter_times."

                lk = ForwardModeling()
                lk.configuration.set_basin_conservation(basin_conservation)
                lk.configuration.set_max_iteration(fm_iter_times)
                lk.configuration.set_print_log(log)

            elif method == Preference.LeakageMethod.Iterative:
                assert (prefilter_param is not None) and (
                        prefilter_type is not None), "Iterative requires parameter prefilter_type and prefilter_params."
                assert shc_unfiltered is not None, "Iterative requires parameter shc_unfiltered."

                lk = Iterative()

                prefilter = get_filter(prefilter_type, prefilter_param, lmax=lmax)
                lk.configuration.set_prefilter(prefilter)
                lk.configuration.set_cs_unfiltered(*shc_unfiltered.get_cs2d())

            else:
                assert False

        else:
            assert False

        lk.configuration.set_basin(basin)
        lk.configuration.set_filter(filtering)
        lk.configuration.set_harmonic(har)

        gqij_corrected = lk.apply_to(self.value, get_grid=True)
        self.value = gqij_corrected

        return self

    def get_leakage(self, leak_type: str, filter_type, filter_params, mask, average=True, lmax: int = None):
        assert leak_type in ("in", "out")
        assert type(mask) in (np.ndarray,) or isinstance(mask, GRD)

        if isinstance(mask, GRD):
            mask_value = mask.value
        elif type(mask) in (np.ndarray,):
            mask_value = mask
        else:
            assert False

        grid_masked = copy.deepcopy(self)

        if leak_type == "in":
            grid_masked.value *= (1 - mask_value)
        elif leak_type == "out":
            grid_masked.value *= mask_value
        else:
            assert False

        shc_masked = grid_masked.to_SHC(lmax=lmax)
        shc_masked.filter(filter_type, filter_params)

        grid_filtered = shc_masked.to_GRD(grid_space=self.get_grid_space())

        if leak_type == "in":
            leakage = grid_filtered.regional_extraction(grid_region=mask_value, average=average)
        elif leak_type == "out":
            leakage = grid_filtered.regional_extraction(grid_region=1 - mask_value, average=average)
        else:
            assert False

        return leakage

    def get_leakage_scale(self, scale_type: str, filter_type, filter_params, mask=None, average=True, lmax: int = None):

        def __fit_scale(x1, x2):
            z = sagea.MathTool.curve_fit(lambda x, k: k * x, x1, x2)
            return z[0][0, 0]

        assert scale_type in ("basin", "grid")
        if scale_type == "basin":
            assert type(mask) in (np.ndarray,) or isinstance(mask, GRD)
        elif scale_type == "grid":
            assert type(mask) in (np.ndarray,) or isinstance(mask, GRD) or mask is None
        else:
            assert False

        grid_masked = copy.deepcopy(self)
        if scale_type == "basin":

            if isinstance(mask, GRD):
                mask_value = mask.value
            elif type(mask) in (np.ndarray,):
                mask_value = mask
            else:
                assert False

            grid_masked.value *= mask_value
            shc_masked = grid_masked.to_SHC(lmax=lmax)
            shc_masked.filter(filter_type, filter_params)
            grid_filtered = shc_masked.to_GRD(grid_space=self.get_grid_space())

            series_unf = self.regional_extraction(grid_region=mask_value, average=average)
            series_fil = grid_filtered.regional_extraction(grid_region=mask_value, average=average)
            scale = __fit_scale(series_fil, series_unf)

            return scale

        elif scale_type == "grid":
            if isinstance(mask, GRD):
                mask_value = mask.value
            elif type(mask) in (np.ndarray,):
                mask_value = mask
            elif mask is None:
                mask_value = np.ones_like(self.value[0])
            else:
                assert False

            scales = np.zeros_like(mask_value)

            if mask_value is not None:
                grid_masked.value *= mask_value

            shc_masked = grid_masked.to_SHC(lmax=lmax)
            shc_masked.filter(filter_type, filter_params)
            grid_filtered = shc_masked.to_GRD(grid_space=self.get_grid_space())

            index_mask = np.array(np.where(mask == 1)).T
            for i in range(len(index_mask)):
                series_unf = self.value[:, index_mask[i][0], index_mask[i][1]]
                series_fil = grid_filtered.value[:, index_mask[i][0], index_mask[i][1]]

                scale = __fit_scale(series_fil, series_unf)
                scales[index_mask[i][0], index_mask[i][1]] = scale

            return scales

        else:
            assert False

    def leakage_fm(self, mask: np.ndarray, filter_type, filter_params: tuple, lmax: int = None,  # necessary params
                   basin_conservation: np.ndarray = None, fm_iter_times: int = 30, log=False):

        # assert basin_conservation is not None, "Forward Modeling requires parameter basin_conservation."
        assert fm_iter_times is not None, "Forward Modeling requires parameter fm_iter_times."

        if lmax is None:
            lmax = int(180 / self.get_grid_space())

        if basin_conservation is None:
            from sagea.pysrc.load_file.LoadL2SH import load_SHC

            shc_ocean = load_SHC(pathlib.Path(__file__).parent / "../../__data__/auxiliary/ocean360_grndline.sh",
                                 lmax=lmax, key="")
            grid_ocean = shc_ocean.to_GRD(grid_space=self.get_grid_space())
            grid_ocean.limiter(0.5, 1, 0)

            basin_conservation = grid_ocean.value[0]

        lk = ForwardModeling()
        lk.configuration.set_basin_conservation(basin_conservation)
        lk.configuration.set_max_iteration(fm_iter_times)
        lk.configuration.set_print_log(log)

        filtering = get_filter(filter_type, filter_params, lmax=lmax)

        grid_space = self.get_grid_space()
        lat, lon = MathTool.get_global_lat_lon_range(grid_space)
        har = Harmonic(lat, lon, lmax, option=1)

        lk.configuration.set_basin(mask)
        lk.configuration.set_filter(filtering)
        lk.configuration.set_harmonic(har)

        gqij_corrected = lk.apply_to(self.value, get_grid=True)
        self.value = gqij_corrected

        return self

    def seismic(self, dates, events: dict):

        sei = SeismicCorrection()
        sei.configuration.set_times(dates)
        sei.configuration.set_earthquakes(events)

        sei.apply_to(self.value, lat=self.lat, lon=self.lon)

        return self

    def de_aliasing(self, dates,
                    s2: bool = False, p1: bool = False, s1: bool = False, k2: bool = False, k1: bool = False):
        de_alias = DeAliasing()

        de_alias.configuration.set_de_s2(s2),
        de_alias.configuration.set_de_p1(p1),
        de_alias.configuration.set_de_s1(s1),
        de_alias.configuration.set_de_k2(k2),
        de_alias.configuration.set_de_k1(k1),

        year_frac = TimeTool.convert_date_format(
            dates, input_type=TimeTool.DateFormat.ClassDate, output_type=TimeTool.DateFormat.YearFraction
        )

        self.value = de_alias.apply_to(self.value, year_frac)

    def __integral_for_one_basin(self, mask=None, average=True):
        assert type(mask) in (np.ndarray,) or isinstance(mask, GRD) or mask is None

        if average:
            assert mask is not None

        if isinstance(mask, GRD):
            assert not mask.is_series()
            mask = mask.value[0]

        if mask is None:
            grids = self.value
        else:
            grids = self.value * mask

        lat, lon = self.lat, self.lon

        integral_result = MathTool.global_integral(grids, lat, lon)

        if average:
            integral_result /= MathTool.get_acreage(mask)

        return integral_result

    def __integral(self, mask=None, average=True):
        assert type(mask) in (np.ndarray,) or isinstance(mask, GRD) or mask is None

        if mask is None:
            return self.__integral_for_one_basin(mask, average=average)

        else:
            if isinstance(mask, GRD):
                mask_value = mask.value
            elif type(mask) in (np.ndarray,):
                mask_value = mask
            else:
                assert False

            assert mask_value.ndim in (2, 3)

            if mask_value.ndim == 2:
                return self.__integral_for_one_basin(mask, average=average)

            else:
                result_list = []
                for i in range(mask_value.shape[0]):
                    result = self.__integral_for_one_basin(mask_value[i], average=average)
                    result_list.append(result)

                return np.array(result_list)

    def regional_extraction(self, grid_region, average=True):
        if isinstance(grid_region, GRD):
            grid_region = grid_region.value

        return self.__integral(grid_region, average=average)

    def limiter(self, threshold=0, beyond=1, below=0):
        index_beyond = np.where(self.value >= threshold)
        index_below = np.where(self.value < threshold)

        self.value[index_beyond] = beyond
        self.value[index_below] = below
        return self

    def to_file(self, filepath: pathlib.Path, rewrite=False, time_dim=None, description=None):
        if not filepath.parent.exists():
            filepath.parent.mkdir(parents=True)
        if filepath.exists() and not rewrite:
            assert False, "file already exists"

        filename = filepath.name
        if "." in filename:
            type_in_name = filename.split(".")[-1]
        else:
            type_in_name = None

        if type_in_name is None:
            filename += ".nc"

        savetype = filename.split(".")[-1]

        types = ("nc", "npz", "hdf5")
        assert savetype in types, f"saving type must be one of {types}"

        if savetype == "nc":
            self.__save_nc(filepath, time_dim=time_dim, value_description=description)

        elif savetype == "npz":
            self.__save_npz(filepath, time_dim=time_dim, value_description=description)

        elif savetype == "hdf5":
            self.__save_hdf5(filepath, time_dim=time_dim, value_description=description)

    def __save_nc(self, filepath: pathlib.Path, time_dim=None, from_date=None, value_description=None):
        assert filepath.name.endswith(".nc")
        assert time_dim is not None
        assert len(time_dim) == np.shape(self.value)[0]

        if from_date is None:
            from_date = datetime.date(1900, 1, 1)

        time_delta = TimeTool.convert_date_format(
            time_dim,
            input_type=TimeTool.DateFormat.ClassDate,
            output_type=TimeTool.DateFormat.TimeDelta,
            from_date=from_date,
        )

        with netCDF4.Dataset(filepath, 'w', format='NETCDF4') as ncfile:
            ncfile.createDimension('time', size=len(time_delta))
            ncfile.createDimension('lat', size=len(self.lat))
            ncfile.createDimension('lon', size=len(self.lon))

            times = ncfile.createVariable('time', int, ('time',))
            latitudes = ncfile.createVariable('lat', np.float32, ('lat',))
            longitudes = ncfile.createVariable('lon', np.float32, ('lon',))
            values = ncfile.createVariable('value', np.float32, ('time', 'lat', 'lon'))

            times[:] = time_delta
            latitudes[:] = self.lat
            longitudes[:] = self.lon
            values[:] = self.value

            times.description = f"days from {from_date}"
            latitudes.description = f"geographical latitude in unit [degree]"
            longitudes.description = f"geographical longitude in unit [degree]"
            if value_description is not None:
                values.description = value_description

        return self

    def __save_npz(self, filepath: pathlib.Path, time_dim=None, from_date=None, value_description=None):
        assert filepath.name.endswith(".npz")
        assert time_dim is not None
        assert len(time_dim) == np.shape(self.value)[0]

        if from_date is None:
            from_date = datetime.date(1900, 1, 1)

        time_delta = TimeTool.convert_date_format(
            time_dim,
            input_type=TimeTool.DateFormat.ClassDate,
            output_type=TimeTool.DateFormat.TimeDelta,
            from_date=from_date,
        )

        np.savez(
            filepath,
            lat=self.lat, lon=self.lon, value=self.value,
            description=value_description,
            date_begin=from_date, days=time_delta,
        )

    def __save_hdf5(self, filepath: pathlib.Path, time_dim=None, from_date=None, value_description=None):
        assert filepath.name.endswith(".hdf5")
        assert time_dim is not None
        assert len(time_dim) == np.shape(self.value)[0]

        if from_date is None:
            from_date = datetime.date(1900, 1, 1)

        time_delta = TimeTool.convert_date_format(
            time_dim,
            input_type=TimeTool.DateFormat.ClassDate,
            output_type=TimeTool.DateFormat.TimeDelta,
            from_date=from_date,
        )

        with h5py.File(filepath, "w") as h5file:
            t_group = h5file.create_group("time")
            t_group.create_dataset("description", data=f"days from {from_date}")
            t_group.create_dataset("data", data=time_delta)

            v_group = h5file.create_group("value")
            if value_description is not None:
                v_group.create_dataset("description", data=value_description)
            v_group.create_dataset("data", data=self.value)

            lat_group = h5file.create_group("lat")
            lat_group.create_dataset("description", data=f"geographical latitude in unit [degree]")
            lat_group.create_dataset("data", data=self.lat)

            lon_group = h5file.create_group("lon")
            lon_group.create_dataset("description", data=f"geographical longitude in unit [degree]")
            lon_group.create_dataset("data", data=self.lon)
